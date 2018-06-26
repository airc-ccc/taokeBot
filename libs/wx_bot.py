# -*-coding: UTF-8-*-

from __future__ import unicode_literals
import re
import configparser
from bs4 import BeautifulSoup
from libs import movie
from libs import orther
from libs import textMessage
from libs import my_utils
from libs import mediaJd
from libs import alimama
from libs import groupMessage
from libs import pingdd

class tbAndJd(object):
    def __init__(self, bot):
        self.logger = my_utils.init_logger()
        self.mjd = mediaJd.MediaJd(bot)
        self.al = alimama.Alimama(self.logger, bot)
        self.movie = movie.SharMovie()
        self.tm = textMessage.TextMessage(bot)
        self.fm = groupMessage.FormData()
        self.ort = orther.Orther()
        self.config = configparser.ConfigParser()
        self.config.read('config.conf',encoding="utf-8-sig")
        self.pdd = pingdd.Pdd(bot)

    # 检查是否是淘宝链接
    def check_if_is_tb_link(self, msg, bot, raw):
        # 判断信息是否是淘口令
        #if re.search(r'【.*】', msg['Text']) and (u'打开👉手机淘宝👈' in msg['Text'] or u'打开👉手淘👈' in msg['Text'] or u'打开👉淘宝👈' in msg['Text'] or u'咑|開👉氵匋 宝👈' in msg['Text']):
        if re.search(r'【.*】', msg['Text']) and (u'👈' in msg['Text'] or u'👉' in msg['Text']):
            # 判断用户是否存在
            res = self.ort.ishaveuserinfo(bot, msg, raw)
            if res['res'] == 'not_info':
                # 不存在就去创建
                self.ort.create_user_info(raw, bot, msg, 0, tool=False)
            # 调用淘宝获取商品优惠信息
            return self.al.getTao(bot, msg, raw)
        elif msg['Type'] == 'Sharing':  # 分享型消息
            res = self.ort.ishaveuserinfo(bot, msg, raw)
            if res['res'] == 'not_info':
                self.ort.create_user_info(raw, bot, msg, 0, tool=False)
            # 获取消息里的xml信息，判断appname是否是电影或京东的分享
            htm = re.findall(r"<appname>.*?</appname>", msg['Content'])
            if htm:
                soup_xml = BeautifulSoup(msg['Content'], 'lxml')
                xml_info = soup_xml.select('appname')
                if xml_info[0].string == "京东":
                    return self.mjd.getJd(raw, bot, msg, msg['Url'])
                elif xml_info[0].string == "拼多多":
                    return self.pdd.getGood(raw, msg)
                else:
                    return self.movie.getMovie(msg)
        elif msg['Type'] == 'Text':  # 关键字查询信息
            return self.tm.getText(raw, bot, msg)

    # 检查是否是淘宝链接
    def check_if_is_group(self, msg, bot, raw):
        #if re.search(r'【.*】', msg['Text']) and (u'打开👉手机淘宝👈' in msg['Text'] or u'打开👉手淘👈' in msg['Text'] or u'打开👉淘宝👈' in msg['Text'] or u'咑|開👉氵匋 宝👈' in msg['Text']) and ():
        if re.search(r'【.*】', msg['Text']) and (u'👈' in msg['Text'] or u'👉' in msg['Text']):
            return self.al.getGroupTao(raw, bot, msg)
        elif msg['Type'] == 'Sharing':
            htm = re.findall(r"<appname>.*?</appname>", msg['Content'])
            if htm:
                soup_xml = BeautifulSoup(msg['Content'], 'lxml')
                xml_info = soup_xml.select('appname')
                if xml_info[0].string == "京东":
                    return self.mjd.getGroupJd(bot, msg, msg['Url'], raw)
                elif xml_info[0].string == "拼多多":
                    return self.pdd.getGroupGood(raw, msg)
                else:
                    return self.movie.getGroupMovie(msg)
        elif msg['Type'] == 'Text':
            return self.tm.getGroupText(bot, msg)
