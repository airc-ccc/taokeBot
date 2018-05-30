# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import requests
import json

config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class SharMovie(object):
    def __init__(self):
        pass

    def getMovie(self, msg):
        soup_xml = BeautifulSoup(msg['Content'], 'lxml')
        xml_info = soup_xml.select('appname')
        # 定义视频网站
        shipin = ['腾讯视频', '爱奇艺', '优酷视频', '芒果 TV', '搜狐视频客户端版']

        for item in shipin:
            if item == xml_info[0].string:
                player_url = config.get('URL', 'movieurl')+'%s' % msg['Url']

                res = self.getShortUrl(player_url)
                text = '''
一一一一 视频信息 一一一一

播放链接：'''+res+'''
                        '''
                return text

    def getGroupMovie(self, msg):
        soup_xml = BeautifulSoup(msg['Content'], 'lxml')
        xml_info = soup_xml.select('appname')
        # 定义视频网站
        shipin = ['腾讯视频', '爱奇艺', '优酷视频', '芒果 TV']

        for item in shipin:
            if item == xml_info[0].string:
                player_url = config.get('URL', 'movieurl')+'%s' % msg['Url']
                res = self.getShortUrl(player_url)
                text = '''
一一一一 视频信息 一一一一

播放链接：'''+res+'''
                        '''
                return text

    # 短链接转换接口
    def getShortUrl(self, longUrl):

        url = "http://47.98.244.9/long2short/long2short.php?longurl="+longUrl+""

        res = requests.get(url)

        rj = json.loads(res.text)
        print(rj)
        return rj['short_url']
