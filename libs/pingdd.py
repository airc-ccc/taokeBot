import os
import json
import time
import platform
import requests
import traceback
import configparser
from bs4 import BeautifulSoup
from libs import my_utils
from selenium import webdriver
from libs.mysql import ConnectMysql

cookie_fname = 'cookies_pdd.txt'
sysstr = platform.system()
class Pdd:
    def __init__(self, bot):
        self.logger = my_utils.init_logger()
        self.se = requests.session()
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read('config.conf',encoding="utf-8-sig")

    def getGood(self, raw, msg):
        cm = ConnectMysql()
        try:
            # 获取商品信息，首先获取商品id
            arr1 = msg['Text'].split('元')
            arr2 = arr1[1].split('拼多多')
            good_id = self.getDetail(arr2[0])
            if good_id == 'GetGoodIdError':
                error_text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+self.config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+self.config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+self.config.get('URL', 'lnvit')+'''
                        '''
                return error_text

            pid = self.getPromotion()

            if pid == 'GetPromotionIdError':
                error_text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+self.config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+self.config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+self.config.get('URL', 'lnvit')+'''
                        '''
                return error_text

            pid = pid['result']['promotionChannelList'][0]['pid']
            res = self.getLink(good_id['result']['goodsList'][0]['goodsId'], pid)

            good = good_id['result']['goodsList'][0]['goodsId']

            # 判断是否有优惠券
            if good_id['result']['goodsList'][0]['hasCoupon'] == True:
                # 原价
                minGroupPrice = float(int(good_id['result']['goodsList'][0]['minGroupPrice']) / 1000)

                # 优惠券
                coupon = int(int(good_id['result']['goodsList'][0]['couponDiscount']) / 1000)

                # 卷后价
                couponPrice = round(float(minGroupPrice - coupon), 2)

                # 返利金额
                backPrice = round(((float(couponPrice * (int(good_id['result']['goodsList'][0]['promotionRate']) / 1000)))) * float(self.config.get('BN', 'bn3p')), 2)
                text = '''
一一一一拼多多返利一一一一

【商品名】%s

【拼多多】%s元
【优惠券】%s元
【劵后价】%s元
【返红包】%s元
领券下单链接:%s

省钱步骤：
1,点击链接，进入下单！
2,订单完成后，将订单完成日期和订单号发给我哦！
例如：
2018-01-01,12345678901
                    ''' % (arr2[0], minGroupPrice, coupon, couponPrice, backPrice, res['result']['shortUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type) VALUES('"+ self.bot.self.nick_name +"', '" + \
                             arr2[0] + "', '" + str(minGroupPrice) + "', '"+str(coupon)+"', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ raw.sender.puid +"', '"+ self.bot.self.puid +"', '"+ str(good) +"', '3')"
                cm.ExecNonQuery(insert_sql)

                return text
            else:
                # 原价
                minGroupPrice = float(int(good_id['result']['goodsList'][0]['minGroupPrice']) / 1000)

                # 返利金额
                backPrice = round(((float(minGroupPrice * (int(good_id['result']['goodsList'][0]['promotionRate']) / 1000)))) * float(self.config.get('BN', 'bn3p')), 2)
                text = '''
一一一一拼多多返利一一一一

【商品名】%s

【拼多多】%s元
【返红包】%s元
下单链接:%s

省钱步骤：
1,点击链接，进入下单！
2,订单完成后，将订单完成日期和订单号发给我哦！
例如：
2018-01-01,12345678901
                    ''' % (arr2[0], minGroupPrice, backPrice, res['result']['shortUrl'])
                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type) VALUES('"+ self.bot.self.nick_name +"', '" + arr2[0] + "', '" + str(minGroupPrice) + "', '0', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ raw.sender.puid +"', '"+ self.bot.self.puid +"', '"+ str(good) +"', '3')"
                cm.ExecNonQuery(insert_sql)

                return text
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))

    def getGroupGood(self, raw, msg):
        cm = ConnectMysql()
        try:
            wei_info = self.bot.core.search_chatrooms(userName=msg['FromUserName'])
            puid = raw.member.puid
            # 获取商品信息，首先获取商品id
            arr1 = msg['Text'].split('元')
            arr2 = arr1[1].split('拼多多')
            good_id = self.getDetail(arr2[0])
            if good_id == 'GetGoodIdError':
                error_text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+self.config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+self.config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+self.config.get('URL', 'lnvit')+'''
                        '''
                return error_text

            pid = self.getPromotion()

            if pid == 'GetPromotionIdError':
                error_text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢

京东优惠券商城：
'''+self.config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+self.config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+self.config.get('URL', 'lnvit')+'''
                        '''
                return error_text

            pid = pid['result']['promotionChannelList'][0]['pid']
            res = self.getLink(good_id['result']['goodsList'][0]['goodsId'], pid)
            good = good_id['result']['goodsList'][0]['goodsId']
            # 判断是否有优惠券
            if good_id['result']['goodsList'][0]['hasCoupon'] == True:
                # 原价
                minGroupPrice = float(int(good_id['result']['goodsList'][0]['minGroupPrice']) / 1000)

                # 优惠券
                coupon = int(int(good_id['result']['goodsList'][0]['couponDiscount']) / 1000)

                # 卷后价
                couponPrice = round(float(minGroupPrice - coupon), 2)

                # 返利金额
                backPrice = round(((float(couponPrice * (int(good_id['result']['goodsList'][0]['promotionRate']) / 1000)))) * float(self.config.get('BN', 'bn3p')), 2)
                text = '''
一一一一拼多多返利一一一一

【商品名】%s

【拼多多】%s元
【优惠券】%s元
【劵后价】%s元
【返红包】%s元
领券下单链接:%s

省钱步骤：
1,点击链接，进入下单！
2,订单完成后，将订单完成日期和订单号发给我哦！
例如：
2018-01-01,12345678901
                    ''' % (arr2[0], minGroupPrice, coupon, couponPrice, backPrice, res['result']['shortUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type, chatroom) VALUES('"+ self.bot.self.nick_name +"', '" + \
                             arr2[0] + "', '" + str(minGroupPrice) + "', '"+str(coupon)+"', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ puid +"', '"+ self.bot.self.puid +"', '"+ str(good) +"', '3', '"+ wei_info['NickName'] +"')"
                cm.ExecNonQuery(insert_sql)

                return text
            else:
                # 原价
                minGroupPrice = float(int(good_id['result']['goodsList'][0]['minGroupPrice']) / 1000)

                # 返利金额
                backPrice = round(((float(minGroupPrice * (int(good_id['result']['goodsList'][0]['promotionRate']) / 1000)))) * float(self.config.get('BN', 'bn3p')), 2)
                text = '''
一一一一拼多多返利一一一一

【商品名】%s

【拼多多】%s元
【返红包】%s元
下单链接:%s

省钱步骤：
1,点击链接，进入下单！
2,订单完成后，将订单完成日期和订单号发给我哦！
例如：
2018-01-01,12345678901
                    ''' % (arr2[0], minGroupPrice, backPrice, res['result']['shortUrl'])
                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type, chatroom) VALUES('"+ self.bot.self.nick_name +"', '" + \
                             arr2[0] + "', '" + str(minGroupPrice) + "', '0', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ puid +"', '"+ self.bot.self.puid +"', '"+ str(good) +"', '3', '"+ wei_info['NickName'] +"')"
                cm.ExecNonQuery(insert_sql)

                return text
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))

    def check_login(self):
        try:
            res = self.getPromotion()
            if res['success'] == False:
                return 'login out'
            return 'login success'
        except:
            return 'login out'

    def login(self):
        clr = self.check_login()

        if 'login success' in clr:
            self.logger.debug('拼多多已登录！不需要再次登录！')
            return 'Login Success'
        else:
            res = self.do_login()
            return res

    def do_login(self):
        if (sysstr == "Linux") or (sysstr == "Darwin"):
            firefoxOptions = webdriver.FirefoxOptions()

            firefoxOptions.set_headless()

            # 开启driver
            wd = webdriver.Firefox(firefox_options=firefoxOptions)
        else:
            wd = webdriver.Firefox()
        wd.get('http://jinbao.pinduoduo.com/#/')

        time.sleep(5)

        wd.find_element_by_class_name('pdd-top-nav-login-btn').click()

        # 输入账号密码
        wd.find_element_by_id('mobile').send_keys(self.config.get('PDD', 'PDD_USERNAME'))
        # 休息3秒
        time.sleep(60)

        # 获取cookie并写入文件
        cookies = wd.get_cookies()
        print(cookies)
        # 写入Cookies文件
        with open(cookie_fname, 'w') as f:
            f.write(json.dumps(cookies))

        wd.quit()

        return 'Login Success'

    def getDetail(self, good_name):
        self.load_cookies()
        try:
            url = 'http://jinbao.pinduoduo.com/network/api/common/goodsList'

            data = {'keyword': good_name,'pageNumber': 1,'pageSize': 60,'sortType': 0,'withCoupon': 0}

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/json; charset=UTF-8'
            }

            # requests POST
            good_res = self.se.post(url=url, data=json.dumps(data), headers=headers)

            good_res = json.loads(good_res.text)

            return good_res
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))
            return 'GetGoodIdError'


    # 获取推广位
    def getPromotion(self):
        self.load_cookies()
        try:
            url = 'http://jinbao.pinduoduo.com/network/api/promotion/promotionList'

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/json; charset=UTF-8'
            }

            data = {'pageNumber': 1, 'pageSize': 200}

            res = self.se.post(url, json.dumps(data), headers=headers)

            res = json.loads(res.text)

            return res
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))
            return 'GetPromotionIdError'

    def getLink(self, goodId, pid):
        self.load_cookies()
        try:
            url = 'http://jinbao.pinduoduo.com/network/api/promotion/createPromotionUrl'

            data = {
                'goodsId': goodId,
                'pid': pid
            }

            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/json; charset=UTF-8'
            }

            res = self.se.post(url=url, data=json.dumps(data), headers=headers)

            res = json.loads(res.text)
            return res
        except Exception as e:
            trace = traceback.format_exc()
            print("error:{},trace:{}".format(str(e), trace))
            return 'GetGoodLinkError'


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
            self.se.cookies.set(c['name'], c['value'])
