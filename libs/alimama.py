# encoding: utf-8

import re
import json
import configparser
import random
import traceback
import requests
from libs.orther import Orther
from libs.movie import SharMovie

cookie_fname = 'cookies_taobao.txt'
config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class Alimama:
    def __init__(self, logger, bot):
        if config.get('SYS', 'tb') == 'yes':
            self.logger = logger
            self.ort = Orther()
            self.movie = SharMovie()
            self.bot2 = bot
            self.se = requests.session()

    def getTao(self, bot, msg, raw):
        if config.get('SYS', 'tb') == 'no':
            text = '''
一一一一系统信息一一一一
机器人在升级中, 暂不支持淘宝商品查询
                    '''
            return text

        try:

            # 获取淘口令
            if '《' in msg['Text'] and '》' not in msg['Text']:
                taokouling = re.search(r'《.*?《', msg['Text']).group()
            elif '￥' in msg['Text']:
                taokouling = re.search(r'￥.*?￥', msg['Text']).group()
            elif '€' in msg['Text']:
                taokouling = re.search(r'€.*?€', msg['Text']).group()

            res = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_wireless_share_tpwd_query.php?str=' + taokouling)
            resj = json.loads(res.text)
            print(resj)
            if 'https://item.taobao.com' in resj['url']:
                potten2 = resj['url'].split('&id=')
                id = potten2[1].split('&sourceType')[0]
            else:
                potten = resj['url'].split('https://a.m.taobao.com/i')
                id = potten[1].split('.htm')[0]
            url3 = 'http://api.hitui.net/privilege?type=1&appkey=JoB3RIns&id=%s&pid=%s&session=%s' % (id, config.get('SYS', 'PID'), config.get('SYS', 'SESSION'))
            print(url3)
            # 获取优惠券链接
            datares = self.se.get(url3)
            coupon_link = json.loads(datares.text)
            coupon_link2 = coupon_link['tbk_privilege_get_response']['result']['data']
            if 'tbk_privilege_get_response' not in coupon_link or 'coupon_info' not in json.dumps(coupon_link):
                if 'price' not in resj:
					# 如果没有佣金，推荐
					# 推荐链接
                    tui_url = 'http://tuijian.ptjob.net/www/public/index.html%23/index/' + id
                    shortUrl = self.movie.getShortUrl(tui_url)
                    text = '''
 一一一一 返利信息 一一一一

 亲，当前商品优惠券已领完，为您精选如下优惠券商品

 精选好券:'''+shortUrl+'''

                                 '''
                    return text

				# 普通商品转淘口令
                taoken2 = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/goodToKen.php?goodid=' + id)
                taoken2 = json.loads(taoken2.text)['data']['taoToken']
                print(taoken2)
				
                # 红包：券后价 * 佣金比例 / 100
                fx2 = round((round(float(resj['price']) * float(coupon_link2['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)
                # 没有优惠券
                res_text = '''
一一一一返利信息一一一一

【商品名】%s

【淘宝价】%s元
【返红包】%.2f元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                                                        ''' % (resj['content'], resj['price'], fx2, taoken2)
                return res_text
            # 获取优惠券金额
            coupon_price = coupon_link2['coupon_info'].split('减')[1].split('元')[0]

            ress=self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title='+resj['content']+'&counp_link='+coupon_link2['coupon_click_url']+'&image_link='+resj['pic_url'], headers={'Connection':'close'})
            # 优惠券链接转淘口令
            urlToToken = json.loads(ress.text)['data']['model']
            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link2['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)

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
            # 获取淘口令
            if '《' in msg['Text'] and '》' not in msg['Text']:
                taokouling = re.search(r'《.*?《', msg['Text']).group()
            elif '￥' in msg['Text']:
                taokouling = re.search(r'￥.*?￥', msg['Text']).group()
            elif '€' in msg['Text']:
                taokouling = re.search(r'€.*?€', msg['Text']).group()

            res = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_wireless_share_tpwd_query.php?str=' + taokouling)
            resj = json.loads(res.text)
            if 'https://item.taobao.com' in resj['url']:
                potten2 = resj['url'].split('&id=')
                id = potten2[1].split('&sourceType')[0]
            else:
                potten = resj['url'].split('https://a.m.taobao.com/i')
                id = potten[1].split('.htm')[0]
            url3 = 'http://api.hitui.net/privilege?type=1&appkey=JoB3RIns&id=%s&pid=%s&session=%s' % (id, config.get('SYS', 'PID'), config.get('SYS', 'SESSION'))
            # 获取优惠券链接
            datares = self.se.get(url3)
            coupon_link = json.loads(datares.text)
            coupon_link2 = coupon_link['tbk_privilege_get_response']['result']['data']
            if 'tbk_privilege_get_response' not in coupon_link or 'coupon_info' not in json.dumps(coupon_link):
                if 'price' not in resj:
					# 如果没有佣金，推荐
					# 推荐链接
                    tui_url = 'http://tuijian.ptjob.net/www/public/index.html%23/index/' + id
                    shortUrl = self.movie.getShortUrl(tui_url)
                    text = '''
 一一一一 返利信息 一一一一

 亲，当前商品优惠券已领完，为您精选如下优惠券商品

 精选好券:'''+shortUrl+'''

                                 '''
                    return text

				# 普通商品转淘口令
                taoken2 = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/goodToKen.php?goodid=' + id)
                taoken2 = json.loads(taoken2.text)['data']['taoToken']
                print(taoken2)
				
                # 红包：券后价 * 佣金比例 / 100
                fx2 = round((round(float(resj['price']) * float(coupon_link2['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)
                # 没有优惠券
                res_text = '''
一一一一返利信息一一一一

【商品名】%s

【淘宝价】%s元
【返红包】%.2f元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                                                        ''' % (resj['content'], resj['price'], fx2, taoken2)
                return res_text

            coupon_link = json.loads(datares.text)['tbk_privilege_get_response']['result']['data']
            # 获取优惠券金额
            coupon_price = coupon_link2['coupon_info'].split('减')[1].split('元')[0]
            ress=self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title='+resj['content']+'&counp_link='+coupon_link2['coupon_click_url']+'&image_link='+resj['pic_url'], headers={'Connection':'close'})
            # 优惠券链接转淘口令
            urlToToken = json.loads(ress.text)['data']['model']
            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link2['max_commission_rate']), 2) / 100) * float(config.get('BN', 'bn3t')), 2)

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
            return info
