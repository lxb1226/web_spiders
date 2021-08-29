import os
import time

import requests
from lxml import etree
from multiprocessing import Pool

# TODO:使用多进程进行下载，还需要学习如何使用，在哪个地方使用

BASE_URL = "https://wallhaven.cc/hot?page="
SAVE_DIR = './images/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}


def get_urls(url):
    resp = requests.get(url, headers=HEADERS)
    html = etree.HTML(resp.text)
    lis = html.xpath('//*[@id="thumbs"]/section[1]/ul/li')
    for li in lis:
        href = li.xpath('./figure/a/@href')
        print(href)
        get_img_url(href[0])


def get_img_url(url):
    resp = requests.get(url, headers=HEADERS)
    html = etree.HTML(resp.text)
    img = html.xpath('//*[@id="wallpaper"]/@src')
    print(img)
    save_img(img[0])


def save_img(url):
    resp = requests.get(url, headers=HEADERS)
    filename = url.split('/')[-1]
    print(filename)
    with open(SAVE_DIR + filename, 'wb') as f:
        f.write(resp.content)


def worker(arg):
    print("子进程开始执行>>> pid={},ppid={},编号:{}".format(os.getpid(), os.getppid(), arg))
    url = BASE_URL + str(arg)
    get_urls(url)


def main():
    print("主进程开始执行>>> pid={}".format(os.getpid()))
    ps = Pool(5)
    for i in range(10):
        ps.apply_async(worker, args=(i,))
    ps.close()
    ps.join()
    print("主进程终止")


if __name__ == '__main__':
    # url = 'https://wallhaven.cc/hot?page=1'
    # get_urls(url)
    main()
