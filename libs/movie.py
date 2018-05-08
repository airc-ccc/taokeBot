# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import requests

config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class SharMovie(object):
    def __init__(self):
        long = "https://media.jd.com/gotoadv/goods?searchId=2011016742%23%23%23st1%23%23%23kt1%23%23%23598e10defb7f41debe6af038e875b61c&pageIndex=&pageSize=50&property=&sort=&goodsView=&adownerType=&pcRate=&wlRate=&category1=&category=&category3=&condition=0&fromPrice=&toPrice=&dataFlag=0&keyword=%E9%9E%8B%E5%AD%90&input_keyword=%E9%9E%8B%E5%AD%90&price=PC"
        self.getShortUrl(long)

    def getMovie(self, msg):
        soup_xml = BeautifulSoup(msg['Content'], 'lxml')
        xml_info = soup_xml.select('appname')
        # 定义视频网站
        shipin = ['腾讯视频', '爱奇艺', '优酷视频', '芒果 TV']

        for item in shipin:
            if item == xml_info[0].string:
                player_url = config.get('URL', 'movieurl')+'%s' % msg['Url']
                text = '''
一一一一 视频信息 一一一一

播放链接：'''+player_url+'''

分享【京东商品链接】或者【淘口令】
精准查询商品优惠券和返利信息！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
免费看电影方法：
'''+config.get('URL', 'movie')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
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
                text = '''
一一一一 视频信息 一一一一

播放链接：'''+player_url+'''

分享【京东商品链接】或者【淘口令】
精准查询商品优惠券和返利信息！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
免费看电影方法：
'''+config.get('URL', 'movie')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                        '''
                return text

    def getShortUrl(self, longUrl):
        pass