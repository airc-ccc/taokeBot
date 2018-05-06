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

class tbAndJd(object):
    def __init__(self):
        self.logger = my_utils.init_logger()
        self.mjd = mediaJd.MediaJd()
        self.al = alimama.Alimama(self.logger)
        self.movie = movie.SharMovie()
        self.tm = textMessage.TextMessage()
        self.fm = groupMessage.FormData()
        self.ort = orther.Orther()
        self.config = configparser.ConfigParser()
        self.config.read('config.conf',encoding="utf-8-sig")

    # 检查是否是淘宝链接
    def check_if_is_tb_link(self, msg, bot, raw):
        if re.search(r'【.*】', msg['Text']) and (
                u'打开👉手机淘宝👈' in msg['Text'] or u'打开👉天猫APP👈' in msg['Text'] or u'打开👉手淘👈' in msg['Text']):
            return self.al.getTao(bot, msg, raw)
        elif msg['Type'] == 'Sharing':  # vip 电影
            res = self.ort.ishaveuserinfo(bot, msg, raw)
            if res['res'] == 'not_info':
                self.ort.create_user_info(raw, bot, msg, 0, tool=False)
            htm = re.findall(r"<appname>.*?</appname>", msg['Content'])
            if htm:
                soup_xml = BeautifulSoup(msg['Content'], 'lxml')
                xml_info = soup_xml.select('appname')
                if xml_info[0].string == "京东":
                    return self.mjd.getJd(raw, bot, msg, msg['Url'])
                else:
                    return self.movie.getMovie(msg)
        elif msg['Type'] == 'Text':  # 关键字查询信息
            return self.tm.getText(raw, bot, msg)

    # 检查是否是淘宝链接
    def check_if_is_group(self, msg, bot, raw):
        if re.search(r'【.*】', msg['Text']) and (
                u'打开👉手机淘宝👈' in msg['Text'] or u'打开👉天猫APP👈' in msg['Text'] or u'打开👉手淘👈' in msg['Text']):
            return self.al.getGroupTao(raw, bot, msg)
        elif msg['Type'] == 'Sharing':
            htm = re.findall(r"<appname>.*?</appname>", msg['Content'])
            if htm:
                soup_xml = BeautifulSoup(msg['Content'], 'lxml')
                xml_info = soup_xml.select('appname')
                if xml_info[0].string == "京东":
                    self.logger.debug(msg)
                    return self.mjd.getGroupJd(bot, msg, msg['Url'], raw)
                else:
                    return self.movie.getGroupMovie(msg)
        elif msg['Type'] == 'Text':
            return self.tm.getGroupText(bot, msg)
