# encoding: utf-8

import os
import re
import json
import os.path
import configparser
import platform
import random
import sys
import time
import traceback
import datetime
if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib

from io import BytesIO
import pyqrcode
import requests
from PIL import Image
from threading import Thread
from libs.mysql import ConnectMysql
from libs.orther import Orther
from libs.movie import SharMovie
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

cookie_fname = 'cookies_taobao.txt'
config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class Alimama:
    def __init__(self, logger, bot):
        if config.get('SYS', 'tb') == 'yes':
            self.se = requests.session()
            # self.load_cookies()
            self.myip = "127.0.0.1"
            # self.start_keep_cookie_thread()
            self.logger = logger
            self.ort = Orther()
            self.movie = SharMovie()
            self.bot2 = bot

        # 加密方法

    def encrypt_oracle(self, value):
        a = ''
        for i in value:
            a = a + str(ord(i)) + '**'

        return a

    def getTao(self, bot, msg, raw):
        if config.get('SYS', 'tb') == 'no':
            text = '''
一一一一系统信息一一一一
机器人在升级中, 暂不支持淘宝商品查询
                    '''
            return text

        try:
            # q = re.search(r'【.*】', msg['Text']).group().replace(u'【', '').replace(u'】', '')
            # if u'打开👉天猫APP👈' in msg['Text']:
            #     try:
            #         url = re.search(r'http://.* \)', msg['Text']).group().replace(u' )', '')
            #     except:
            #         url = None
            #
            # else:
            #     try:
            #         url = re.search(r'http://.* ，', msg['Text']).group().replace(u' ，', '')
            #     except:
            #         url = None

            # if url is None:
            #     taokoulingurl = 'http://www.taokouling.com/index.php?m=api&a=taokoulingjm'
            #     if '《' in msg['Text']:
            #         taokouling = re.search(r'《.*?《', msg['Text']).group()
            #     elif '￥' in msg['Text']:
            #         taokouling = re.search(r'￥.*?￥', msg['Text']).group()
            #     elif '€' in msg['Text']:
            #         taokouling = re.search(r'€.*?€', msg['Text']).group()
            #     parms = {'username': 'wx_tb_fanli', 'password': 'wx_tb_fanli', 'text': taokouling}
            #     res = requests.post(taokoulingurl, data=parms)
            #     url = res.json()['url'].replace('https://', 'http://')

            # real_url = self.get_real_url(url)
            #
            # res = self.get_detail(bot, real_url, raw)

            # 获取淘口令
            taokoulin = ''
            if '《' in msg['Text']:
                taokouling = re.search(r'《.*?《', msg['Text']).group()
            elif '￥' in msg['Text']:
                taokouling = re.search(r'￥.*?￥', msg['Text']).group()
            elif '€' in msg['Text']:
                taokouling = re.search(r'€.*?€', msg['Text']).group()

            # res = requests.get('http://api.hitui.net/Kl_Query?appkey=JoB3RIns&content=' + taokouling)
            res = requests.get('http://123.56.217.225:8082/taobao_wireless_share_tpwd_query.php?str=' + taokouling)
            resj = json.loads(res.text)
            print(resj)
            id = ''
            urlToToken=''
            if 'https://item.taobao.com' in resj['url']:
                potten2 = resj['url'].split('&id=')
                id = potten2[1].split('&sourceType')[0]
            else:
                potten = resj['url'].split('https://a.m.taobao.com/i')
                id = potten[1].split('.htm')[0]
            print('idididiidididiidididiididid', id)
            # 获取优惠券链接
            datares = requests.get('http://api.hitui.net/privilege?type=1&appkey=JoB3RIns&id=%s&pid=%s&session=%s' % (id, config.get('SYS', 'PID'), config.get('SYS', 'SESSION')))
            coupon_link = json.loads(datares.text)
            if 'tbk_privilege_get_response' not in coupon_link or 'coupon_info' not in json.dumps(coupon_link):
                text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                                '''
                return text

            coupon_link = json.loads(datares.text)['tbk_privilege_get_response']['result']['data']
            # 获取优惠券金额
            coupon_price = coupon_link['coupon_info'].split('减')[1].split('元')[0]

            couurl = f"http://api.hitui.net/Kl_Create?appkey=JoB3RIns&text={resj['content']}&url={coupon_link['coupon_click_url']}&logo={resj['pic_url']}"
            # 优惠券链接转淘口令
            ress = requests.get(couurl)
            urlToToken = json.loads(ress.text)['model']
            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)

            # 更换符号
            tu = {0: '🗝', 1: '📲', 2: '🎵'}
            n = random.randint(0, 2)
            tao_token = urlToToken.replace(urlToToken[:1], tu[n])
            tao_token = tao_token.replace(tao_token[-1:], tu[n])

            res_text = '''
一一一一返利信息一一一一

【商品名】%s

【淘宝价】%s元
【优惠券】%s元
【返红包】%.2f元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                                        ''' % (resj['content'], resj['price'], coupon_price, fx, tao_token)
            return res_text
#             if res == 'no match item':
#                 text = '''
# 一一一一 返利信息 一一一一
#
# 亲，当前商品暂无优惠券,建议您换一个商品试试呢
#
# 京东优惠券商城：
# '''+config.get('URL', 'jdshop')+'''
# 淘宝优惠券商城：
# '''+config.get('URL', 'tbshop')+'''
# 邀请好友得返利说明：
# '''+config.get('URL', 'lnvit')+'''
#                                 '''
#                 return text
#
#             auctionid = res['auctionId']
#             coupon_amount = res['couponAmount']
#             price = res['zkPrice']
#
#             # 佣金
#             yongjin = price - coupon_amount
#             if config.get('SYS', 'isHighServant') == 'yes':
#                 fx2 = round((yongjin * float(res['tkRate']) / 100) * float(config.get('BN', 'bn3t')), 2)
#             else:
#                 fx2 = round((yongjin * float(res['tkCommonRate']) / 100) * float(config.get('BN', 'bn3t')), 2)
#             real_price = round(price - coupon_amount, 2)
#             res1 = self.get_tk_link(auctionid)
#             tu = {0: '🗝', 1: '📲', 2: '🎵'}
#             n = random.randint(0, 2)
#             tao_token = res1['taoToken'].replace(res1['taoToken'][:1], tu[n])
#             tao_token = tao_token.replace(tao_token[-1:], tu[n])
#             # asciistr2 = self.encrypt_oracle(tao_token)
#             # longurl2 = 'http://txq.ptjob.net/goodCouponToken?value=' + asciistr2 + 'image=' + res['pictUrl'] + 'title=' + res['title'] + 'coupon_url=' + res1['clickUrl']
#             # shorturl2 = self.movie.getShortUrl(longurl2)
#
#             coupon_link = res1['couponLink']
#             if coupon_link != "":
#                 coupon_token = res1['couponLinkTaoToken'].replace(res1['couponLinkTaoToken'][:1], tu[n])
#                 coupon_token = coupon_token.replace(coupon_token[-1:], tu[n])
#                 # asciistr = self.encrypt_oracle(coupon_token)
#                 # longurl = 'http://txq.ptjob.net/goodCouponToken?value='+asciistr + 'image=' + res['pictUrl'] + 'title=' + res['title'] + 'coupon_url=' + res1['couponLink']
#                 # shorturl = self.movie.getShortUrl(longurl)
#                 res_text = '''
# 一一一一返利信息一一一一
#
# 【商品名】%s元
#
# 【淘宝价】%s元
# 【优惠券】%s元
# 【券后价】%s元
# 【返红包】%.2f元
# 【淘链接】%s
#
# 获取返红包步骤：
# 1,复制本条消息打开淘宝领券
# 2,下完单后复制订单号发给我
#                         ''' % (q, price, coupon_amount, real_price, fx2, coupon_token)
#             else:
#                 res_text = '''
# 一一一一返利信息一一一一
#
# 【商品名】%s
# 【淘宝价】%s元
# 【返红包】%.2f元
# 【淘链接】%s
#
# 获取返红包步骤：
# 1,复制本条消息打开淘宝领券
# 2,下完单后复制订单号发给我
#                                         ''' % (q, price, fx2, tao_token)
#             return res_text
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))
            info = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢,您也可以在下边的优惠券商城中查找哦

京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                    '''
            return info

    def getGroupTao(self, raw, bot, msg):
        if config.get('SYS', 'tb') == 'no':
            text = '''
一一一一系统信息一一一一
机器人在升级中, 暂不支持淘宝商品查询
                    '''
            return text
        try:
#             q = re.search(r'【.*】', msg['Text']).group().replace(u'【', '').replace(u'】', '')
#             if u'打开👉天猫APP👈' in msg['Text']:
#                 try:
#                     url = re.search(r'http://.* \)', msg['Text']).group().replace(u' )', '')
#                 except:
#                     url = None
#
#             else:
#                 try:
#                     url = re.search(r'http://.* ，', msg['Text']).group().replace(u' ，', '')
#                 except:
#                     url = None
#
#             if url is None:
#                 taokoulingurl = 'http://www.taokouling.com/index.php?m=api&a=taokoulingjm'
#                 if '《' in msg['Text']:
#                     taokouling = re.search(r'《.*?《', msg['Text']).group()
#                 elif '￥' in msg['Text']:
#                     taokouling = re.search(r'￥.*?￥', msg['Text']).group()
#                 elif '€' in msg['Text']:
#                     taokouling = re.search(r'€.*?€', msg['Text']).group()
#                 parms = {'username': 'wx_tb_fanli', 'password': 'wx_tb_fanli', 'text': taokouling}
#                 res = requests.post(taokoulingurl, data=parms)
#                 url = res.json()['url'].replace('https://', 'http://')
#
#             real_url = self.get_real_url(url)
#
#             res = self.get_group_detail(bot, real_url, raw)
#             if res == 'no match item':
#                 text = '''
# 一一一一 返利信息 一一一一
#
# 亲，当前商品暂无优惠券,建议您换一个商品试试呢
#
#
# 京东优惠券商城：
# '''+config.get('URL', 'jdshop')+'''
# 淘宝优惠券商城：
# '''+config.get('URL', 'tbshop')+'''
# 邀请好友得返利说明：
# '''+config.get('URL', 'lnvit')+'''fdasfsf
#                                 '''
#                 return text
#
#             auctionid = res['auctionId']
#             coupon_amount = res['couponAmount']
#             price = res['zkPrice']
#             # 佣金
#             yongjin = price - coupon_amount
#             if config.get('SYS', 'isHighServant') == 'yes':
#                 fx2 = round((yongjin * float(res['tkRate']) / 100) * float(config.get('BN', 'bn3t')), 2)
#             else:
#                 fx2 = round((yongjin * float(res['tkCommonRate']) / 100) * float(config.get('BN', 'bn3t')), 2)
#             real_price = round(price - coupon_amount, 2)
#             res1 = self.get_tk_link(auctionid)
#
#             # tao_token = res1['taoToken']
#             # asciistr2 = self.encrypt_oracle(tao_token)
#             #
#             # longurl2 = 'http://txq.ptjob.net/goodCouponToken?value=' + asciistr2 + 'image=' + res[
#             #     'pictUrl'] + 'title=' + res['title'] + 'coupon_url=' + res1['clickUrl']
#             # shorturl2 = self.movie.getShortUrl(longurl2)
#
#             tu = {0: '🗝', 1: '📲', 2: '🎵'}
#             n = random.randint(0, 2)
#             tao_token = res1['taoToken'].replace(res1['taoToken'][:1], tu[n])
#             tao_token = tao_token.replace(tao_token[-1:], tu[n])
#
#             coupon_link = res1['couponLink']
#             if coupon_link != "":
#                 # coupon_token = res1['couponLinkTaoToken']
#                 # asciistr = self.encrypt_oracle(coupon_token)
#                 # longurl = 'http://txq.ptjob.net/goodCouponToken?value=' + asciistr + 'image=' + res[
#                 #     'pictUrl'] + 'title=' + res['title'] + 'coupon_url=' + res1['couponLink']
#                 # shorturl = self.movie.getShortUrl(longurl)
#                 coupon_token = res1['couponLinkTaoToken'].replace(res1['couponLinkTaoToken'][:1], tu[n])
#                 coupon_token = coupon_token.replace(coupon_token[-1:], tu[n])
#
#                 res_text = '''
# 一一一一淘宝返利信息一一一一
#
# 【商品名】%s元
#
# 【淘宝价】%s元
# 【优惠券】%s元
# 【券后价】%s元
# 【返红包】%.2f元
# 【淘链接】%s
#
# 获取返红包步骤：
# 1,复制本条消息打开淘宝领券
# 2,点击头像添加机器人为好友
# 3,下完单后复制订单号发给我
#                                         ''' % (q, price, coupon_amount, real_price, fx2, coupon_token)
#             else:
#                 res_text = '''
# 一一一一淘宝返利信息一一一一
#
# 【商品名】%s
# 【淘宝价】%s元
# 【返红包】%.2f元
# 【淘链接】%s
#
# 获取返红包步骤：
# 1,复制本条消息打开淘宝领券
# 2,点击头像添加机器人为好友
# 3,下完单后复制订单号发给我
#                         ''' % (q, price, fx2, tao_token)
#             return res_text
            # 获取淘口令
            taokoulin = ''
            if '《' in msg['Text']:
                taokouling = re.search(r'《.*?《', msg['Text']).group()
            elif '￥' in msg['Text']:
                taokouling = re.search(r'￥.*?￥', msg['Text']).group()
            elif '€' in msg['Text']:
                taokouling = re.search(r'€.*?€', msg['Text']).group()


            res = requests.get('http://123.56.217.225:8082/taobao_wireless_share_tpwd_query.php?str=' + taokouling)
            resj = json.loads(res.text)
            id = ''
            urlToToken=''
            if 'https://item.taobao.com' in resj['url']:
                potten2 = resj['url'].split('&id=')
                id = potten2[1].split('&sourceType')[0]
            else:
                potten = resj['url'].split('https://a.m.taobao.com/i')
                id = potten[1].split('.htm')[0]
            # 获取优惠券链接
            datares = requests.get('http://api.hitui.net/privilege?type=1&appkey=JoB3RIns&id=%s&pid=%s&session=%s' % (id, config.get('SYS', 'PID'), config.get('SYS', 'SESSION')))
            coupon_link = json.loads(datares.text)
            if 'tbk_privilege_get_response' not in coupon_link or 'coupon_info' not in json.dumps(coupon_link):
                text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                                '''
                return text

            coupon_link = json.loads(datares.text)['tbk_privilege_get_response']['result']['data']
            # 获取优惠券金额
            coupon_price = coupon_link['coupon_info'].split('减')[1].split('元')[0]

            couurl = f"http://api.hitui.net/Kl_Create?appkey=JoB3RIns&text={resj['content']}&url={coupon_link['coupon_click_url']}&logo={resj['pic_url']}"
            # 优惠券链接转淘口令
            ress = requests.get(couurl)
            urlToToken = json.loads(ress.text)['model']
            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)

            # 更换符号
            tu = {0: '🗝', 1: '📲', 2: '🎵'}
            n = random.randint(0, 2)
            tao_token = urlToToken.replace(urlToToken[:1], tu[n])
            tao_token = tao_token.replace(tao_token[-1:], tu[n])

            res_text = '''
一一一一返利信息一一一一

【商品名】%s

【淘宝价】%s元
【优惠券】%s元
【返红包】%.2f元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,点击头像添加机器人为好友
3,下完单后复制订单号发给我
                                        ''' % (resj['content'], resj['price'], coupon_price, fx, tao_token)
            return res_text
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))
            info = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢。


京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                    '''
            return res_text

    # 启动一个线程，定时访问淘宝联盟主页，防止cookie失效
    def start_keep_cookie_thread(self):
        t = Thread(target=self.visit_main_url, args=())
        t.setDaemon(True)
        t.start()

    def start_keep_get_order(self, bot):
        t = Thread(target=self.getOrderInfo, args=(bot,))
        t.setDaemon(True)
        t.start()

    def visit_main_url(self):
        url = "https://pub.alimama.com/"
        headers = {
            'method': 'GET',
            'authority': 'pub.alimama.com',
            'scheme': 'https',
            'path': '/common/getUnionPubContextInfo.json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        while True:
            time.sleep(60 * 5)
            try:
                self.get_url(url, headers)
                real_url = "https://detail.tmall.com/item.htm?id=42485910384"
                res = self.get_detail2(real_url)
                print('淘宝登录验证.....', res)
            except Exception as e:
                # 给管理员发送登录过期消息
                adminuser = self.bot2.friends().search(config.get('ADMIN', 'ADMIN_USER'))[0]
                text = '''
                ---------- 系统提醒 ----------

                机器人【%s】, 淘宝登录失效
                                    ''' % (self.bot2.self.nick_name)
                adminuser.send(text)
                trace = traceback.format_exc()
                self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 获取商品详情
    def get_detail2(self, q):
        cm = ConnectMysql()
        try:
            t = int(time.time() * 1000)
            tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
            pvid = '10_%s_1686_%s' % (self.myip, t)
            url = 'http://pub.alimama.com/items/search.json?q=%s&_t=%s&auctionTag=&perPageSize=40&shopTag=&t=%s&_tb_token_=%s&pvid=%s' % (
                urllib.quote(q.encode('utf8')), t, t, tb_token, pvid)
            headers = {
                'method': 'GET',
                'authority': 'pub.alimama.com',
                'scheme': 'https',
                'path': '/items/search.json?%s' % url.split('search.json?')[-1],
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                'referer': 'https://pub.alimama.com',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
            }
            res = self.get_url(url, headers)
            rj = res.json()
            if rj['data']['pageList'] != None:
                return rj['data']['pageList'][0]
            else:
                return 'no match item'
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    def get_url(self, url, headers):
        res = self.se.get(url, headers=headers)
        return res

    def post_url(self, url, headers, data):
        res = self.se.post(url, headers=headers, data=data)
        return res

    def load_cookies(self):
        if os.path.isfile(cookie_fname):
            with open(cookie_fname, 'r') as f:
                c_str = f.read().strip()
                self.set_cookies(c_str)

    def set_cookies(self, c_str):
        try:
            cookies = json.loads(c_str)
        except:
            return
        for c in cookies:
            self.se.cookies.set(c[0], c[1])

    # check login
    def check_login(self):
        url = 'https://pub.alimama.com/common/getUnionPubContextInfo.json'
        headers = {
            'method': 'GET',
            'authority': 'pub.alimama.com',
            'scheme': 'https',
            'path': '/common/getUnionPubContextInfo.json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }

        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text)
        return rj

    def visit_login_rediret_url(self, url):
        headers = {
            'method': 'GET',
            'authority': 'login.taobao.com',
            'scheme': 'https',
            'path': '/member/loginByIm.do?%s' % url.split('loginByIm.do?')[-1],
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        self.logger.debug(res.status_code)

    def get_scan_qr_status(self, lg_token):
        defaulturl = 'http://login.taobao.com/member/taobaoke/login.htm?is_login=1'
        url = 'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=%s&defaulturl=%s&_ksTS=%s_30&callback=jsonp31' % (
            lg_token, defaulturl, int(time.time() * 1000))
        headers = {
            'method': 'GET',
            'authority': 'qrlogin.taobao.com',
            'scheme': 'https',
            'path': '/qrcodelogin/qrcodeLoginCheck.do?%s' % url.split('qrcodeLoginCheck.do?')[-1],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'accept': '*/*',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text.replace('(function(){jsonp31(', '').replace(');})();', ''))
        self.logger.debug(rj)
        return rj

    def show_qr_image(self):
        self.logger.debug('begin to show qr image')
        url = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?from=alimama&_ksTS=%s_30&callback=jsonp31' % int(
            time.time() * 1000)

        # get qr image
        headers = {
            'method': 'GET',
            'authority': 'qrlogin.taobao.com',
            'scheme': 'https',
            'path': '/qrcodelogin/generateQRCode4Login.do?%s' % url.split('generateQRCode4Login.do?')[-1],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'accept': '*/*',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh-CN,zh;q=0.8',
        }

        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text.replace('(function(){jsonp31(', '').replace(');})();', ''))
        lg_token = rj['lgToken']
        url = 'https:%s' % rj['url']

        headers = {
            'method': 'GET',
            'authority': 'img.alicdn.com',
            'scheme': 'https',
            'path': '/tfscom/%s' % url.split('tfscom/')[-1],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'accept': 'image/webp,image/*,*/*;q=0.8',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        qrimg = BytesIO(res.content)
        self.logger.debug(u"begin qr")

        sysstr = platform.system()
        if (sysstr == "Windows"):
            # windows下可能无法打印请用下列代码
            img = Image.open(qrimg)
            img.show()

        elif (sysstr == "Linux") or (sysstr == "Darwin"):
            # 读取url
            import zbarlight
            img = Image.open(qrimg)
            codes = zbarlight.scan_codes('qrcode', img)
            qr_url = codes[0]
            # 使用pyqrcode在终端打印，只在linux下可以用
            pyqrcode_url = pyqrcode.create(qr_url)
            self.logger.debug(pyqrcode_url.terminal())

        self.logger.debug(u"请使用淘宝客户端扫码")
        return lg_token

    def get_qr_image(self):
        url = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?from=alimama&_ksTS=%s_30&callback=jsonp31' % int(
            time.time() * 1000)

        # get qr image
        headers = {
            'method': 'GET',
            'authority': 'qrlogin.taobao.com',
            'scheme': 'https',
            'path': '/qrcodelogin/generateQRCode4Login.do?%s' % url.split('generateQRCode4Login.do?')[-1],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'accept': '*/*',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
        }

        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text.replace('(function(){jsonp31(', '').replace(');})();', ''))
        lg_token = rj['lgToken']
        url = 'https:%s' % rj['url']

        headers = {
            'method': 'GET',
            'authority': 'img.alicdn.com',
            'scheme': 'https',
            'path': '/tfscom/%s' % url.split('tfscom/')[-1],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'accept': 'image/webp,image/*,*/*;q=0.8',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        qrimg = BytesIO(res.content)
        self.logger.debug("TaoBao Login Out!")
        return qrimg

    # do login
    def do_login(self):
        self.logger.debug('begin to login')
        # show qr image
        lg_token = self.show_qr_image()
        t0 = time.time()
        while True:
            rj = self.get_scan_qr_status(lg_token)
            # 扫码成功会有跳转
            if 'url' in rj:
                self.visit_login_rediret_url(rj['url'])
                self.logger.debug('login success')
                # self.logger.debug(self.se.cookies)
                with open(cookie_fname, 'w') as f:
                    f.write(json.dumps(self.se.cookies.items()))
                return 'login success'
            # 二维码过一段时间会失效
            if time.time() - t0 > 60 * 5:
                self.logger.debug('scan timeout')
                return
            time.sleep(0.5)

    def login(self):
        try:
            clr = self.check_login()
            print('Checking login ...............', clr)
            self.myip = clr['data']['ip']
            if 'mmNick' in clr['data']:
                self.logger.debug(u"淘宝已经登录 不需要再次登录")
                return 'login success'
            else:
                dlr = self.open_do_login()
                if dlr is None:
                    return 'login failed'
                else:
                    return 'login success'
        except Exception as e:
            trace = traceback.format_exc()
            return 'login failed'

    def open_do_login(self):
        # loginname = input('请输入淘宝联盟账号:')
        # nloginpwd = input('请输入淘宝联盟密码:')
        #profileDir = "C:\\Users\pengtao\AppData\Local\Mozilla\Firefox\Profiles\\24xolutj.default"

        #profile = webdriver.FirefoxProfile(profileDir)
        #print(profile)
        #wd = webdriver.Firefox(profile)
        wd = webdriver.Firefox()

        wd.get('http://pub.alimama.com')

        time.sleep(20)

        #js = "var pass = document.getElementById(\"TPL_password_1\").setAttribute(\"autocomplete\", \"on\")"

        #wd.execute_script(js)
        wd.switch_to.frame('taobaoLoginIfr')
        time.sleep(3)
        wd.find_element_by_class_name('login-switch').click()
        time.sleep(3)
        # 输入账号密码
        wd.find_element_by_id('TPL_username_1').send_keys(config.get('TB', 'TB_USERNAME'))
        # 休息3秒
        time.sleep(3)
        # 输入密码
        wd.find_element_by_id('TPL_password_1').send_keys(config.get('TB', 'TB_PASSWORD'))
        # 点击登录按钮
        time.sleep(2)
        while True:
            # 定位滑块元素
            source = wd.find_element_by_xpath("//*[@id='nc_1_n1z']")
            # 定义鼠标拖放动作
            ActionChains(wd).drag_and_drop_by_offset(source, 400, 0).perform()

            # 等待JS认证运行,如果不等待容易报错
            time.sleep(2)

            text = wd.find_element_by_xpath("//div[@id='nc_1__scale_text']/span")
            # 目前只碰到3种情况：成功（请在在下方输入验证码,请点击图）；无响应（请按住滑块拖动)；失败（哎呀，失败了，请刷新）
            if text.text.startswith(u'哎呀，出错了，点击'):
                print('滑动失败！Begin to try.....')
                # 这里定位失败后的刷新按钮，重新加载滑块模块
                wd.find_element_by_xpath("//div[@id='havana_nco']/div/span/a").click()
                time.sleep(3)
                continue
        wd.find_element_by_id('J_SubmitStatic').click()

        # 判断是否需要验证码
        # time.sleep(10)

        # if self.isElementExist(wd, 'J_LoginCheck'):
        #     print('验证码存在！睡眠120秒')
        #     time.sleep(160)

        # self.logger.debug('login success')
        # with open(cookie_fname, 'w') as f:
        #     cookies_arr = []
        #     for item in wd.get_cookies():
        #         cookies_arr.append([item['name'], item['value']])
        #
        #     f.write(json.dumps(cookies_arr))
        #
        # wd.quit()
        #
        # return 'login success'

    def isElementExist(self, bower, element):
        try:
            bower.find_element_by_id(element)
            return True
        except Exception as e:
            return False

    def get_tb_token(self):
        tb_token = None
        for c in self.se.cookies.items():
            if c[0] == '_tb_token_':
                return c[1]
        if tb_token is None:
            return 'test'

    # 获取商品详情
    def get_detail(self, bot, q, raw):
        cm = ConnectMysql()
         # 用户第一次查询，修改备注
        query_good = cm.ExecQuery("SELECT * FROM taojin_query_record WHERE puid='" + raw.sender.puid + "' AND bot_puid='" + bot.self.puid + "'")

        if query_good == ():
            se = re.compile('^(\d+)_(\d+)_\w_(\d)+$')
            if se.search(raw.sender.remark_name) == None:
                remarkName = self.ort.generateRemarkName(bot)
                split_arr2 = remarkName.split('_')
                new_remark_name2 = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', 'B', '_', split_arr2[3])
                bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name2)
                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name2+"' WHERE puid='" + raw.sender.puid + "' AND bot_puid='" + bot.self.puid + "'")
            else:
                split_arr = raw.sender.remark_name.split('_')
                new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'B', '_', split_arr[3])
                bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name)

                # 修改数据库
                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + raw.sender.puid + "' AND bot_puid='" + bot.self.puid + "'")
        try:
            t = int(time.time() * 1000)
            tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
            pvid = '10_%s_1686_%s' % (self.myip, t)
            url = 'http://pub.alimama.com/items/search.json?q=%s&_t=%s&auctionTag=&perPageSize=40&shopTag=&t=%s&_tb_token_=%s&pvid=%s' % (
                urllib.quote(q.encode('utf8')), t, t, tb_token, pvid)
            headers = {
                'method': 'GET',
                'authority': 'pub.alimama.com',
                'scheme': 'https',
                'path': '/items/search.json?%s' % url.split('search.json?')[-1],
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                'referer': 'https://pub.alimama.com',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.5',
            }
            res = self.get_url(url, headers)
            rj = res.json()
            if rj['data']['pageList'] != None:
                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type) VALUES('" + bot.self.nick_name + "', '" + rj['data']['pageList'][0]['title'] + "', '" + str(rj['data']['pageList'][0]['zkPrice']) + "', '"+ str(rj['data']['pageList'][0]['couponAmount']) +"', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+raw.sender.puid+"', '"+bot.self.puid+"', '"+ str(rj['data']['pageList'][0]['auctionId']) +"', '2')"
                cm.ExecNonQuery(insert_sql)
                cm.Close()
                return rj['data']['pageList'][0]
            else:
                return 'no match item'
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 获取商品详情
    def get_group_detail(self, bot, q, raw):
        cm = ConnectMysql()
        chatrooms = bot.core.search_chatrooms(userName=raw.raw['FromUserName'])
        try:
            t = int(time.time() * 1000)
            tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
            pvid = '10_%s_1686_%s' % (self.myip, t)
            url = 'http://pub.alimama.com/items/search.json?q=%s&_t=%s&auctionTag=&perPageSize=40&shopTag=&t=%s&_tb_token_=%s&pvid=%s' % (
                urllib.quote(q.encode('utf8')), t, t, tb_token, pvid)
            headers = {
                'method': 'GET',
                'authority': 'pub.alimama.com',
                'scheme': 'https',
                'path': '/items/search.json?%s' % url.split('search.json?')[-1],
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                'referer': 'https://pub.alimama.com',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.5',
            }
            res = self.get_url(url, headers)
            rj = res.json()
            if rj['data']['pageList'] != None:
                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, chatroom, skuid, type) VALUES('" + bot.self.nick_name + "', '" + rj['data']['pageList'][0]['title'] + "', '" + str(rj['data']['pageList'][0]['zkPrice']) + "', '"+ str(rj['data']['pageList'][0]['couponAmount']) +"', '" + raw.member.nick_name + "', '" + str(time.time()) + "', '"+ raw.member.puid +"', '"+ bot.self.puid +"', '"+ chatrooms['NickName'] +"', '"+ str(rj['data']['pageList'][0]['auctionId']) +"', '2')"
                cm.ExecNonQuery(insert_sql)
                cm.Close()
                return rj['data']['pageList'][0]
            else:
                return 'no match item'
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 获取淘宝客链接
    def get_tk_link(self, auctionid):
        t = int(time.time() * 1000)
        tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
        pvid = '10_%s_1686_%s' % (self.myip, t)
        try:
            gcid, siteid, adzoneid = self.__get_tk_link_s1(auctionid, tb_token, pvid)
            self.__get_tk_link_s2(gcid, siteid, adzoneid, auctionid, tb_token, pvid)
            res = self.__get_tk_link_s3(auctionid, adzoneid, siteid, tb_token, pvid)
            return res
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 第一步，获取推广位相关信息
    def __get_tk_link_s1(self, auctionid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/adzone/newSelfAdzone2.json?tag=29&itemId=%s&blockId=&t=%s&_tb_token_=%s&pvid=%s' % (
            auctionid, int(time.time() * 1000), tb_token, pvid)
        headers = {
            'Host': 'pub.alimama.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        rj = res.json()
        gcid = rj['data']['otherList'][0]['gcid']
        siteid = rj['data']['otherList'][0]['siteid']
        adzoneid = rj['data']['otherAdzones'][0]['sub'][0]['id']
        return gcid, siteid, adzoneid

    # post数据
    def __get_tk_link_s2(self, gcid, siteid, adzoneid, auctionid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/adzone/selfAdzoneCreate.json'
        data = {
            'tag': '29',
            'gcid': gcid,
            'siteid': siteid,
            'selectact': 'sel',
            'adzoneid': adzoneid,
            't': int(time.time() * 1000),
            '_tb_token_': tb_token,
            'pvid': pvid,
        }
        headers = {
            'Host': 'pub.alimama.com',
            'Content-Length': str(len(json.dumps(data))),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://pub.alimama.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }

        res = self.post_url(url, headers, data)
        return res

    # 获取口令
    def __get_tk_link_s3(self, auctionid, adzoneid, siteid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=%s&adzoneid=%s&siteid=%s&scenes=1&t=%s&_tb_token_=%s&pvid=%s' % (
            auctionid, adzoneid, siteid, int(time.time() * 1000), tb_token, pvid)
        headers = {
            'Host': 'pub.alimama.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        rj = json.loads(res.text)
        return rj['data']

    def get_real_url(self, url):
        try:
            headers = {
                'Host': url.split('http://')[-1].split('/')[0],
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
            }
            res = self.get_url(url, headers)
            if re.search(r'itemId\":\d+', res.text):
                item_id = re.search(r'itemId\":\d+', res.text).group().replace('itemId":', '').replace('https://',
                                                                                                       'http://')
                r_url = "https://detail.tmall.com/item.htm?id=%s" % item_id
            elif re.search(r"var url = '.*';", res.text):
                r_url = re.search(r"var url = '.*';", res.text).group().replace("var url = '", "").replace("';",
                                                                                                           "").replace(
                    'https://', 'http://')
            else:
                r_url = res.url
            if 's.click.taobao.com' in r_url:
                r_url = self.handle_click_type_url(r_url)
            else:
                while ('detail.tmall.com' not in r_url) and ('item.taobao.com' not in r_url) and (
                            'detail.m.tmall.com' not in r_url):
                    headers1 = {
                        'Host': r_url.split('http://')[-1].split('/')[0],
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
                    }
                    res2 = self.get_url(r_url, headers1)
                    self.logger.debug("{},{},{},{}".format(res2.url, res2.status_code, res2.history, res2.text))
                    r_url = res2.url

            return r_url
        except Exception as e:
            self.logger.warning(str(e))
            return url

    def handle_click_type_url(self, url):
        # step 1
        headers = {
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        self.logger.debug("{},{},{}".format(res.url, res.status_code, res.history))
        url2 = res.url

        # step 2
        headers2 = {
            'referer': url,
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url2.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res2 = self.get_url(url2, headers2)
        self.logger.debug("{},{},{}".format(res2.url, res2.status_code, res2.history))
        url3 = urllib.unquote(res2.url.split('t_js?tu=')[-1])

        # step 3
        headers3 = {
            'referer': url2,
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url3.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res3 = self.get_url(url3, headers3)
        self.logger.debug("{},{},{}".format(res3.url, res3.status_code, res3.history))
        r_url = res3.url

        return r_url

    def get_order(self, bot, msg, orderId, userInfo, puid, raw):

        timestr = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        order_id = int(orderId)

        cm = ConnectMysql()

        check_order_sql = "SELECT * FROM taojin_order WHERE order_id='" + str(order_id) + "' AND bot_puid = '" +bot.self.puid+ "';"
        check_order_res = cm.ExecQuery(check_order_sql)

        # 判断该订单是否已经提现
        if len(check_order_res) >= 1:
            cm.Close()
            sendtext ='''
一一一一 订单消息 一一一一

订单【%s】提交成功，请勿重复提交
            ''' % (msg['Text'])
            return sendtext

        cm.ExecNonQuery("INSERT INTO taojin_order(wx_bot, username, order_id, completion_time, order_source, puid, bot_puid, status) VALUES('"+ bot.self.nick_name +"', '"+str(userInfo['NickName'])+"', '"+str(order_id)+"', '" + str(timestr) + "', '1', '"+ puid +"', '"+ bot.self.puid +"', '1')")

        send_text ='''
一一一一 订单消息 一一一一

订单【%s】提交成功，请耐心等待订单结算
结算成功后机器人将自动返利到您个人账户

        ''' % (order_id)
        return send_text

    def changeInfo(self, bot, msg, info, order_id, userInfo, timestr, puid, raw):
        try:
            cm = ConnectMysql()

            # 查询用户是否有上线
            check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';"
            check_user_res = cm.ExecQuery(check_user_sql)

            # 判断是否已经有个人账户，没有返回信息
            if len(check_user_res) < 1:
                cm.Close()
                return {"info":"not_info"}
            else:

                # 获取商品查询记录
                get_query_sql = "SELECT * FROM taojin_query_record WHERE good_title='" + info['auctionTitle'] + "'AND puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"' ORDER BY create_time LIMIT 1;"

                get_query_info = cm.ExecQuery(get_query_sql)

                if get_query_info == ():
                    user_text = '''
    一一一一订单信息一一一一

    返利失败，订单信息有误

                    '''
                    return {'info': 'not_order', 'user_text': user_text}

                # 定义SQL语句 查询用户是否已经存在邀请人
                # 判断是否已经有邀请人了
                if check_user_res and check_user_res[0][17] != '0':

                    # 获取邀请人信息
                    get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';"

                    get_parent_info = cm.ExecQuery(get_parent_sql)

                    # 计算返佣
                    add_balance = round(float(info['feeString']) * float(config.get('BN', 'bn3t')), 2)
                    # 累加余额
                    withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                    # 累加淘宝总返利
                    taobao_rebate_amount = round(float(check_user_res[0][8]) + add_balance, 2)
                    # 累加总返利
                    total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                    jishen = (float(get_query_info[0][4]) - float(info['realPayFeeString']))

                    if jishen < 0:
                        jishen = 0

                    # 计算共节省金额,商品原价减去实际支付价格，加上原有节省金额加上返佣
                    save_money = round(check_user_res[0][10] + jishen + add_balance, 2)
                    # 总订单数加一
                    total_order_num = int(check_user_res[0][11]) + 1
                    # 淘宝订单数加一
                    taobao_order_num = int(check_user_res[0][13]) + 1

                    # 邀请人返利金额
                    add_parent_balance = round(float(info['feeString']) * float(config.get('BN', 'bn4')), 2)

                    # 给邀请人好友返利加上金额
                    friends_rebatr = float(get_parent_info[0][19]) + float(add_balance)
                    # 邀请人总钱数加上返利金额
                    withdrawals_amount2 = round(float(get_parent_info[0][9]) + float(add_balance) * float(config.get('BN', 'bn4')), 2)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount) + "', save_money='"+ str(save_money) +"', taobao_rebate_amount='"+ str(taobao_rebate_amount) +"', total_rebate_amount='"+ str(total_rebate_amount) +"', order_quantity='"+str(total_order_num)+"', taobao_order_quantity='"+str(taobao_order_num)+"', update_time='"+str(time.time())+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")
                    cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount2) + "', friends_rebate='"+str(friends_rebatr)+"', update_time='"+str(time.time())+"' WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';")

                    select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                    # 订单已完成，修改备注
                    order_num = cm.ExecQuery(select_order_num)

                    if order_num == ():
                        split_arr = raw.sender.remark_name.split('_')
                        new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                        bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name)

                        cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                    cm.ExecNonQuery("INSERT INTO taojin_order(wx_bot, username, order_id, completion_time, order_source, puid, bot_puid) VALUES('"+ bot.self.nick_name +"', '"+str(userInfo['NickName'])+"', '"+str(order_id)+"', '" + str(timestr) + "', '2', '"+ puid +"', '"+ bot.self.puid +"')")

                    # 累计订单数量
                    order_nums = cm.ExecQuery(select_order_num)

                    split_arr2 = raw.sender.remark_name.split('_')

                    new_remark_name2 = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                    bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name2)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name2+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                    args = {
                        'wx_bot': bot.self.nick_name,
                        'bot_puid': bot.self.puid,
                        'username': check_user_res[0][4],
                        'puid': puid,
                        'rebate_amount': add_balance,
                        'type': 3,
                        'create_time': time.time()
                    }


                    # 写入返利日志
                    cm.InsertRebateLog(args)
                    parent_puid = self.ort.getPuid(bot, get_parent_info[0][4])
                    args2 = {
                        'wx_bot': bot.self.nick_name,
                        'bot_puid': bot.self.puid,
                        'username': get_parent_info[0][4],
                        'puid': parent_puid,
                        'rebate_amount': add_parent_balance,
                        'type': 4,
                        'create_time': time.time()
                    }


                    # 写入返利日志
                    cm.InsertRebateLog(args2)

                    parent_user_text = '''
    一一一一  推广信息 一一一一

    您的好友【%s】又完成了一笔订单
    返利提成%s元已发放到您个人账户
    回复【个人信息】可查询账户信息
                    ''' % (check_user_res[0][4], add_parent_balance)

                    user_text = '''
    一一一一系统消息一一一一

    订单【%s】已完成
    返利金%s元已发放到您的个人账户
    回复【个人信息】可查询账户信息
    回复【提现】可申请账户余额提现
                    ''' % (order_id, add_balance)
                    cm.Close()
                    return {'parent_user_text': parent_user_text, 'user_text': user_text, 'info': 'success', 'parent': get_parent_info[0][4]}
                else:
                    add_balance = round(float(info['feeString']) * float(config.get('BN', 'bn3t')), 2)
                    withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                    taobao_rebate_amount = round(float(check_user_res[0][8]) + add_balance, 2)
                    total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                    jishen = (float(get_query_info[0][4]) - float(info['realPayFeeString']))

                    if jishen < 0:
                        jishen = 0

                    save_money = round(check_user_res[0][10] + (float(get_query_info[0][4]) - float(info['realPayFeeString'])) + add_balance, 2)
                    total_order_num = int(check_user_res[0][11]) + 1
                    taobao_order_num = int(check_user_res[0][13]) + 1

                    cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                        withdrawals_amount) + "', save_money='" + str(save_money) + "', taobao_rebate_amount='" + str(
                        taobao_rebate_amount) + "', total_rebate_amount='" + str(
                        total_rebate_amount) + "', order_quantity='"+str(total_order_num)+"', taobao_order_quantity='"+str(taobao_order_num)+"', update_time='" + str(time.time()) + "' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")


                    select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                    # 订单已完成，修改备注
                    order_num = cm.ExecQuery(select_order_num)

                    if order_num == ():
                        split_arr = raw.sender.remark_name.split('_')
                        new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                        self.logger.debug(new_remark_name)
                        bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name)

                        cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                    cm.ExecNonQuery("INSERT INTO taojin_order(wx_bot, username, order_id, completion_time, order_source, puid, bot_puid) VALUES('"+ bot.self.nick_name+"', '"+str(userInfo['NickName'])+"', '"+str(order_id)+"', '" + str(timestr) + "', '2', '"+puid+"', '"+bot.self.puid+"')")

                    # 累计订单数量
                    order_nums = cm.ExecQuery(select_order_num)

                    split_arr2 = raw.sender.remark_name.split('_')

                    new_remark_name2 = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                    bot.core.set_alias(userName=raw.sender.user_name, alias=new_remark_name2)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name2+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                    args = {
                        'wx_bot': bot.self.nick_name,
                        'bot_puid': bot.self.puid,
                        'username': check_user_res[0][4],
                        'puid': puid,
                        'rebate_amount': add_balance,
                        'type': 3,
                        'create_time': time.time()
                    }


                    # 写入返利日志
                    cm.InsertRebateLog(args)

                    user_text = '''
    一一一一系统消息一一一一

    订单【%s】已完成
    返利金%s元已发放到您的个人账户
    回复【个人信息】可查询账户信息
    回复【提现】可申请账户余额提现
                                ''' % (order_id, add_balance)
                    cm.Close()
                    return {'user_text': user_text, 'info': 'not_parent_and_success'}
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            return {'info': 'feild'}

    # 定时获取淘宝订单信息
    def getOrderInfo(self, bot):
        self.load_cookies()

        endTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        startTime = str((datetime.date.today() - datetime.timedelta(days=1)))

        t = str(round(time.time()))

        url = "http://pub.alimama.com/report/getTbkPaymentDetails.json?startTime="+startTime+"&endTime="+endTime+"&payStatus=3&queryType=1&toPage=1&perPageSize=50&total=&t="+t+"&pvid=&_tb_token_=f8b388e3f3e37&_input_charset=utf-8"

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "pub.alimama.com",
            "Pragma": "no-cache",
            "Referer": "http://pub.alimama.com/myunion.htm?spm=a219t.7900221/1.a214tr8.2.3d7c75a560ieiE",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
            "X-Requested-With": "XMLHttpRequest"
        }

        while True:
            # 间隔3个小时
            time.sleep(10)
            try:
                # 请求订单接口
                res = self.get_url(url, headers)
                # 格式转化一下
                res_dict = json.loads(res.text)
            except Exception as e:
                self.logger.debug(e)
                return e

if __name__ == '__main__':
    al = Alimama()
    # al.login()
    # q = u'现货 RS版 树莓派3代B型 Raspberry Pi 3B 板载wifi和蓝牙'
    # q = u'蔻斯汀玫瑰身体护理套装沐浴露身体乳爽肤水滋润全身保湿补水正品'
    # q = u'DIY个性定制T恤 定做工作服短袖 男女夏季纯棉广告文化衫Polo印制'
    q = u'防晒衣女2017女装夏装新款印花沙滩防晒服薄中长款大码白色短外套'
    # res = al.get_detail(q)
    # auctionid = res['auctionId']
    # al.get_tk_link(auctionid)
    # url = 'http://c.b1wt.com/h.SQwr1X?cv=kzU8ZvbiEa8&sm=796feb'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S9fQZb?cv=zcNtZvbH4ak&sm=79e4be'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S9gdyy?cv=RW5EZvbuYBw&sm=231894'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S8ppn7?cv=ObUrZvZ3oH9&sm=1b02f8'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.SQ70kv?cv=L5HpZv0w4hJ'
    # url = 'http://c.b1wt.com/h.S9A0pK?cv=8grnZvYkU14&sm=efb5b7'
    url = 'http://zmnxbc.com/s/nlO3j?tm=95b078'
    al.get_real_url(url)
