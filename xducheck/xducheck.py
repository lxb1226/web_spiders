#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import json
import requests
import smtplib
from email.mime.text import MIMEText  # 文本
from email.header import Header
import time
import datetime

MAIL_HOST = "smtp.163.com"  # 指定SMTP服务器
MAIL_SENDER = "xiaobaoluo1998@163.com"  # 发件人
MAIL_PASS = "JOVAFPKLDZUKSFEQ"  # 授权码 并非密码，具体授权码开启方式百度，非常简单
MAIL_RECEIVERS = ['1944303766@qq.com']  # 收件人们


def submit(data):
    conn = requests.Session()
    # Login
    result = conn.post('https://xxcapp.xidian.edu.cn/uc/wap/login/check',
                       data={'username': data['_u'], 'password': data['_p']})
    if result.status_code != 200:
        print('认证大失败')
        exit()
    # Submit
    del data['_u']
    del data['_p']

    result = conn.post('https://xxcapp.xidian.edu.cn/xisuncov/wap/open-report/save', data=data)
    return result.text


def generate_data(user):
    data = {}
    data.update({"_u": user['username']})
    data.update({"_p": user['password']})

    data.update({"sfzx": 1})
    # 定位
    data.update({
        "geo_api_info": '{"type":"complete","position":{"Q":23.285822043836,"R":113.606406850871,"lng":113.6064068,"lat":23.2858220},"location_type":"html5","message":"Get ipLocation failed.Get geolocation success.Convert Success.Get address success.","accuracy":65,"isConverted":true,"status":1,"addressComponent":{"citycode":"020","adcode":"440112","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"九龙大道","streetNumber":"108号","country":"中国","province":"广东省","city":"广州市","district":"黄埔区","township":"九龙镇"},"formattedAddress":"广东省广州市黄埔区九龙镇御禾田公寓广州绿地城","roads":[],"crosses":[],"pois":[],"info":"SUCCESS"}'})

    geo = json.loads(data["geo_api_info"])
    data.update({"address": geo["formattedAddress"],
                 "area": geo["addressComponent"]["province"] + ' ' + geo["addressComponent"]["city"] + ' ' +
                         geo["addressComponent"]["district"], "province": geo["addressComponent"]["province"],
                 "city": geo["addressComponent"]["city"]})

    if data["city"].strip() == "" and data["province"] in ["北京市", "上海市", "重庆市", "天津市"]:
        data["city"] = data["province"]
    # 体温范围
    data.update({"tw": 0})

    # 今日是否出现发热、乏力、干咳、呼吸困难等症状
    data.update({"sfyzz": 0})

    # 是否处于隔离期
    data.update({"sfcyglq": 0})

    # 一码通颜色
    data.update({"ymtys": 0})

    # 其他信息
    data.update({"qtqk": ""})

    return data


def send_email(email, msg, subject):
    message = MIMEText(msg, 'plain', 'utf-8')  # 参数分别为文本，格式，编码
    message['From'] = MAIL_SENDER
    message['To'] = email

    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(MAIL_HOST, 25)
        smtpObj.login(MAIL_SENDER, MAIL_PASS)
        smtpObj.sendmail(MAIL_SENDER, MAIL_RECEIVERS, message.as_string())
        print('send success')
    except smtplib.SMTPException:
        print('send error')


if __name__ == '__main__':
    with open('info.txt', 'r') as f:
        user_info = {}
        line = f.readline().split(' ')
        user_info['username'] = line[0]
        user_info['password'] = line[1]
        user_info['email'] = line[2]

        text = submit(generate_data(user_info))
        print(text)
        curr_hour = datetime.datetime.now().hour
        if 5 < curr_hour < 12:
            subject = "晨检"
        elif 12 <= curr_hour < 1:
            subject = "午检"
        else:
            subject = "晚检"
        subject = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + subject + "成功"
        send_email(user_info['email'], text, subject)

