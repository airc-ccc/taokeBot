# -*- coding: UTF-8 -*-
# author Mr.Peng

import requests
import time
from threading import Thread
import json
import platform
import datetime
import traceback
import re
import os
import configparser
from selenium import webdriver
from libs import my_utils
from bs4 import BeautifulSoup
from time import strftime,gmtime
from libs.mysql import ConnectMysql
from libs.orther import Orther
from libs.tuling import tuling


cookie_fname = 'cookies_jd.txt'
sysstr = platform.system()
config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class MediaJd:
    def __init__(self, bot):
        if config.get('SYS', 'jd') == 'yes':
            self.se = requests.session()
            self.start_keep_cookie_thread()
            self.load_cookies()
            self.ort = Orther()
            self.tu = tuling()
            self.logger = my_utils.init_logger()

    # 启动一个线程，定时访问京东主页，防止cookie失效
    def start_keep_cookie_thread(self):
        t = Thread(target=self.visit_main_url, args=())
        t.setDaemon(True)
        t.start()

    def getJd(self, raw, bot, msg, good_url):
        if config.get('SYS', 'jd') == 'no':
            text = '''
一一一一系统信息一一一一

亲，暂不支持京东链接哦
                    '''
            return text

        cm = ConnectMysql()
        try:
            # 用户第一次查询，修改备注
            query_good = cm.ExecQuery("SELECT * FROM taojin_query_record WHERE puid='"+raw.sender.puid+"' AND bot_puid='"+bot.self.puid+"'")
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

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + raw.sender.puid + "' AND bot_puid='" + bot.self.puid + "'")

            print('开始查询分享商品的信息......'+msg['Text'])

            bot_puid = bot.self.puid

            sku_arr = good_url.split('https://item.m.jd.com/product/')

            if sku_arr == None:
                if config.get('SYS', 'tl') == 'yes':
                    msg_text = self.tu.tuling(msg)
                    return msg_text
                else:
                    return

            sku = sku_arr[1].split('.')
            res = self.get_good_link(sku[0])

            if res['data']['shotCouponUrl'] == '':
                text = '''
一一一一京东返利信息一一一一

【商品名】%s

【京东价】%s元
【返红包】%s元
 返利链接:%s

获取返红包步骤：
1,点击商品链接并进行下单
2,下完单后复制订单号发给我
                    ''' % (res['logTitle'], res['logUnitPrice'], res['rebate'], res['data']['shotUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type) VALUES('"+ bot.self.nick_name +"', '" + \
                             res['logTitle'] + "', '" + str(res['logUnitPrice']) + "', '0', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ raw.sender.puid +"', '"+ bot_puid +"', '"+ res['skuid'] +"', '1')"
                cm.ExecNonQuery(insert_sql)
                return text
            else:
                text = '''
一一一一京东返利信息一一一一

【商品名】%s

【京东价】%s元
【优惠券】%s元
【券后价】%s元
【返红包】%s元
 领券链接:%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                    ''' % (
                res['logTitle'], res['logUnitPrice'], res['youhuiquan_price'], res['coupon_price'], res['rebate'],
                res['data']['shotCouponUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, skuid, type) VALUES('"+ bot.self.nick_name +"', '" + \
                             res['logTitle'] + "', '" + str(res['logUnitPrice']) + "', '" + res['coupon_price2'] + "', '" + raw.sender.nick_name + "', '" + str(time.time()) + "', '"+ raw.sender.puid +"', '"+ bot_puid +"', '"+ res['skuid'] +"', '1')"
                cm.ExecNonQuery(insert_sql)

                return text
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢,您也可以在下边的优惠券商城中查找哦

京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                            '''
            return text

    def getGroupJd(self, bot, msg, good_url, raw):
        if config.get('SYS', 'jd') == 'no':
            text = '''
一一一一系统信息一一一一

亲，暂不支持京东链接
                    '''
            return text
        cm = ConnectMysql()
        try:
            wei_info = bot.core.search_chatrooms(userName=msg['FromUserName'])
            puid = raw.member.puid
            bot_puid = bot.self.puid
            sku_arr = good_url.split('https://item.m.jd.com/product/')
            if sku_arr == None:
                return

            sku = sku_arr[1].split('.')
            res = self.get_good_link(sku[0])
            if res['data']['shotCouponUrl'] == '':
                text = '''
一一一一京东返利信息一一一一

【商品名】%s

【京东价】%s元
【返红包】%s元
 返利链接:%s

获取返红包步骤：
1,点击商品链接并进行下单
2,点击头像添加机器人好友
3,下完单后复制订单号发给我
                            ''' % (res['logTitle'], res['logUnitPrice'], res['rebate'], res['data']['shotUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, chatroom, skuid, type) VALUES('"+ bot.self.nick_name +"', '" + \
                             res['logTitle'] + "', '" + str(res['logUnitPrice']) + "', '0', '" + msg[
                                 'ActualNickName'] + "', '" + str(time.time()) + "', '"+ puid +"', '"+ bot_puid +"', '"+ wei_info['NickName'] +"', '"+ res['skuid'] +"', '1')"
                cm.ExecNonQuery(insert_sql)
                return text
            else:
                text = '''
一一一一京东返利信息一一一一

【商品名】%s

【京东价】%s元
【优惠券】%s元
【券后价】%s元
【返红包】%s元
 领券链接:%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,点击头像添加机器人好友
3,下完单后复制订单号发给我
                                    ''' % (
                    res['logTitle'], res['logUnitPrice'], res['youhuiquan_price'], res['coupon_price'], res['rebate'],
                    res['data']['shotCouponUrl'])

                insert_sql = "INSERT INTO taojin_query_record(wx_bot, good_title, good_price, good_coupon, username, create_time, puid, bot_puid, chatroom, skuid, type) VALUES('"+ bot.self.nick_name +"', '" + \
                             res['logTitle'] + "', '" + str(res['logUnitPrice']) + "', '" + res['coupon_price2'] + "', '" + \
                             msg['ActualNickName'] + "', '" + str(time.time()) + "', '"+ puid +"', '"+ bot_puid +"', '"+ wei_info['NickName'] +"', '"+ res['skuid'] +"', '1')"
                cm.ExecNonQuery(insert_sql)
                return text
        except Exception as e:
            text = '''
一一一一 返利信息 一一一一

亲，当前商品暂无优惠券,建议您换一个商品试试呢,您也可以在下边的优惠券商城中查找哦

京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                            '''
            return text

    def visit_main_url(self):
        self.load_cookies()
        url = "https://media.jd.com/gotoadv/goods?searchId=2011016742%23%23%23st1%23%23%23kt1%23%23%23598e10defb7f41debe6af038e875b61c&pageIndex=&pageSize=50&property=&sort=&goodsView=&adownerType=&pcRate=&wlRate=&category1=&category=&category3=&condition=0&fromPrice=&toPrice=&dataFlag=0&keyword=10960504678&input_keyword=10960504678&price=PC"
        while True:
            time.sleep(60 * 3)
            try:
                # 搜索商品
                res = self.se.get(url)
                # 使用BeautifulSoup解析HTML，并提取属性数据
                soup = BeautifulSoup(res.text, 'lxml')
                a = soup.select('.extension-btn')
                if not len(a):
                    print('京东登录失效 正在重新登录京东')
                    self.login()
            except Exception as e:
                self.login()
                trace = traceback.format_exc()
                print("error:{},trace:{}  京东登录失效 正在重新登录京东".format(str(e), trace))

    def check_login(self):

        self.load_cookies()

        url = 'https://media.jd.com/gotoadv/goods?pageSize=50'

        res = self.se.get(url)

        # 使用BeautifulSoup解析HTML，并提取登录属性，判断登录是否失效
        soup = BeautifulSoup(res.text, 'lxml')

        login = soup.select('.tips')

        # 判断登录状态是否失效
        if len(login) > 0:
            return 'Login Failed'
        else:
            return 'Login Success'

    def do_login(self):
        if (sysstr == "Linux") or (sysstr == "Darwin"):
            firefoxOptions = webdriver.FirefoxOptions()

            firefoxOptions.set_headless()

            # 开启driver
            wd = webdriver.Firefox(firefox_options=firefoxOptions)
        else:
            wd = webdriver.Firefox()
        wd.get('https://passport.jd.com/common/loginPage?from=media&ReturnUrl=https%3A%2F%2Fmedia.jd.com%2FloginJump')
        # 输入账号密码
        wd.find_element_by_id('loginname').send_keys(config.get('JD', 'JD_USERNAME'))
        # 休息3秒
        time.sleep(3)
        # 输入密码
        wd.find_element_by_id('nloginpwd').send_keys(config.get('JD', 'JD_PASSWORD'))
        # 点击登录按钮
        time.sleep(10)
        wd.find_element_by_id('paipaiLoginSubmit').click()
        # 获取cookie并写入文件
        cookies = wd.get_cookies()
        # 写入Cookies文件
        with open(cookie_fname, 'w') as f:
            f.write(json.dumps(cookies))
        time.sleep(5)
        wd.quit()


        return 'Login Success'

    def login(self):
        clr = self.check_login()
        if 'Login Success' in clr:
            print('京东已登录！不需要再次登录！')
            return 'Login Success'
        else:
            self.do_login()

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

    def get_good_link(self, good_name):
        self.load_cookies()
        try:
            uu = "https://media.jd.com/gotoadv/goods?searchId=2011016742%23%23%23st1%23%23%23kt1%23%23%23598e10defb7f41debe6af038e875b61c&pageIndex=&pageSize=50&property=&sort=&goodsView=&adownerType=&pcRate=&wlRate=&category1=&category=&category3=&condition=0&fromPrice=&toPrice=&dataFlag=0&keyword=" + good_name + "&input_keyword=" + good_name + "&price=PC"
            # 搜索商品
            res = self.se.get(uu)
            # 使用BeautifulSoup解析HTML，并提取属性数据
            soup = BeautifulSoup(res.text, 'lxml')
            a = soup.select('.extension-btn')
            coupon = soup.find(attrs={'style':'color: #ff5400;'})
            coupon_price = 0;
            if coupon != None:
                coupon_text = coupon.string
                coupon_price = coupon_text.split('减')[1]

            request_id = soup.select('#requestId')

            str_onclick = a[0].get('onclick')

            string = str_onclick[13:-8]

            arr = string.split(',')

            dict_str = {}
            for item in arr:
                str = item.split('\':')
                str_b = str[0].split('\r\n')
                str_1 = str_b[1].strip()
                str_2 = str_1.split('\'')
                str_3 = str[1].split('\'')

                if len(str_3) >= 2:
                    dict_str[str_2[1]] = str_3[1]
                else:
                    dict_str[str_2[1]] = str_3[0]

            # 拼装FormData
            dict_str['adtType'] = 31
            dict_str['siteName'] = -1
            dict_str['unionWebId'] = -1
            dict_str['protocol'] = 1
            dict_str['codeType'] = 2
            dict_str['type'] = 1
            dict_str['positionId'] = 1194027498
            dict_str['positionName'] = '京推推推广位'
            dict_str['sizeId'] = -1
            dict_str['logSizeName'] = -1
            dict_str['unionAppId'] = -1
            dict_str['unionMediaId'] = -1
            dict_str['materialType'] = 1
            dict_str['orienPlanId'] = -1
            dict_str['landingPageType'] = -1
            dict_str['adOwner'] = 'z_0'
            dict_str['saler'] = -1
            dict_str['isApp'] = -1
            dict_str['actId'] = dict_str['materialId']
            dict_str['wareUrl'] = dict_str['pcDetails']
            dict_str['category'] = dict_str['logCategory']
            dict_str['requestId'] = request_id[0].get('value')

            # 删除多余的属性
            dict_str.pop('logCategory')
            dict_str.pop('pcDetails')
            dict_str.pop('mDetails')

            # 获取领券链接和下单链接
            good_link = self.se.post('https://media.jd.com/gotoadv/getCustomCodeURL', data=dict_str)

            good_text = json.loads(good_link.text)
            good_text['logTitle'] = dict_str['logTitle']
            good_text['logUnitPrice'] = dict_str['logUnitPrice']
            good_text['imgUrl'] = dict_str['imgUrl']
            good_text['skuid'] = dict_str['materialId']
            rebate = float(dict_str['pcComm']) / 100
            if coupon != None:
                good_text['coupon_price'] = round(float(good_text['logUnitPrice']) - int(coupon_price), 2)
                good_text['youhuiquan_price'] = coupon_price
                good_text['rebate'] = round(float(good_text['coupon_price']) * rebate * float(config.get('BN', 'bn3j')), 2)
            else:
                good_text['rebate'] = round(float(good_text['logUnitPrice']) * rebate * float(config.get('BN', 'bn3j')), 2)

            good_text['coupon_price2'] = coupon_price
            return good_text
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    def get_good_info(self, bot):
        cm = ConnectMysql()
        self.load_cookies()
        page = 1
        sku_num = 0
        while sku_num < 20:
            url = "https://media.jd.com/gotoadv/goods?searchId=2011005331%23%23%23st3%23%23%23kt0%23%23%2378dc30b6-fa14-4c67-900c-235b129ab4bb&pageIndex="+str(page)+"&pageSize=50&property=&sort=&goodsView=&adownerType=&pcRate=&wlRate=&category1=&category=&category3=&condition=1&fromPrice=&toPrice=&dataFlag=0&keyword=&input_keyword=&hasCoupon=1&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC&price=PC"
            page += 1
            self.logger.debug(page)
            res = self.se.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            skuList = []
            for li in soup.find_all('li', skuid = re.compile('^[0-9]+$')):
                sku = li.get('skuid')

                exists_sql = "SELECT * FROM taojin_good_info WHERE skuid='"+str(sku)+"' AND bot_puid='"+ bot.self.puid +"';"
                is_exists = cm.ExecQuery(exists_sql)
                if len(is_exists) != 0:
                    print('0....')
                    continue

                sku_num += 1
                skuList.append(sku)

            if skuList == []:
                print('[]....')
                continue

            for item in skuList:
                link_info = self.get_good_link(str(item))
                # item_image = link_info['data']['qRcode']
                item_image = link_info['imgUrl']
                # 请求图片
                res_img = requests.get(item_image)
                img_name = item_image.split('/')
                # 拼接图片名
                file_name = "images/" + img_name[-1]
                fp = open(file_name, 'wb')
                # 写入图片
                fp.write(res_img.content)
                fp.close()
                if link_info['data']['shotCouponUrl'] == '':
                    continue
                else:
                    sql = "INSERT INTO taojin_good_info(wx_bot, skuid, title, image, price, rebate, yhq_price, coupon_price, shoturl, shotcouponurl, status, create_time, bot_puid) VALUES('"+ bot.self.nick_name +"', '" + str(
                        item) + "', '" + str(link_info['logTitle']) + "', '" + str(item_image) + "', '" + str(
                        link_info['logUnitPrice']) + "', '" + str(link_info['rebate']) + "', '" + str(
                        link_info['youhuiquan_price']) + "', '" + str(link_info['coupon_price']) + "', '" + str(
                        link_info['data']['shotUrl']) + "', '" + str(
                        link_info['data']['shotCouponUrl']) + "', '1', '" + str(time.time()) + "', '"+ bot.self.puid +"')"

                cm.ExecNonQuery(sql)

        print("insert success!")

    def get_jd_order(self, bot, msg, orderId, userInfo, puid, raw):
        # try:
        order_id = int(orderId)
        timestr = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        cm = ConnectMysql()

        # 查询订单是否已经提现过了
        check_order_sql = "SELECT * FROM taojin_order WHERE order_id='" + str(order_id) + "' AND bot_puid='"+ bot.self.puid +"' AND puid='"+puid+"';"
        check_order_res = cm.ExecQuery(check_order_sql)

        # 判断该订单是否已经提现
        if len(check_order_res) >= 1:
            cm.Close()
            sendtext = '''
一一一一 订单消息 一一一一

订单【%s】提交成功，请勿重复提交
                        ''' % (order_id)
            return sendtext

        cm.ExecNonQuery("INSERT INTO taojin_order(wx_bot, username, order_id, completion_time, order_source, puid, bot_puid, status) VALUES('"+ str(bot.self.nick_name) +"', '" + str(userInfo['NickName']) + "', '" + str(order_id) + "', '" + str(timestr) + "', '2', '"+puid+"', '"+ bot.self.puid +"', '1')")

        send_text ='''
一一一一 订单消息 一一一一

订单【%s】提交成功，请耐心等待订单结算
结算成功后机器人将自动返利到您个人账户
        ''' % (order_id)
        return send_text
