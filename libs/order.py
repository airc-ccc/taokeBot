# encoding: utf-8

import os
import csv
import json
import os.path
import requests
import traceback
import time,datetime
import sched
import xlrd
from libs import my_utils
from threading import Thread
from libs import mediaJd
from libs import alimama
from libs import orther
from libs import pingdd
from libs.mysql import ConnectMysql
import configparser

c_tb_file = 'cookies_taobao.txt'
c_jd_file = 'cookies_jd.txt'
c_pdd_file = 'cookies_pdd.txt'

class Order:
    def __init__(self, bot):
        self.tb_se = requests.session()
        self.jd_se = requests.session()
        self.pdd_se = requests.session()
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read('config.conf',encoding="utf-8-sig")
        self.logger = my_utils.init_logger()
        self.mjd = mediaJd.MediaJd(self.bot)
        self.al = alimama.Alimama(self.logger, self.bot)
        self.ort = orther.Orther()
        self.pdd = pingdd.Pdd(self.bot)
        self.start_keep_get_alimama_order()
        self.start_keep_get_jd_order()
        self.start_keep_get_pdd_order()

    def load_cookies(self, cookie_fname, jot):
        if os.path.isfile(cookie_fname):
            with open(cookie_fname, 'r') as f:
                c_str = f.read().strip()
                self.set_cookies(c_str, jot)

    def set_cookies(self, c_str, jdortb):
        try:
            cookies = json.loads(c_str)
        except Exception as e:
            print(e)
            return
        for c in cookies:
            jdortb.cookies.set(c[0], c[1])

    def jd_load_cookies(self, cookie_fname, jop):
        if os.path.isfile(cookie_fname):
            with open(cookie_fname, 'r') as f:
                c_str = f.read().strip()
                self.jd_set_cookies(c_str, jop)

    def jd_set_cookies(self, c_str, jop2):
        try:
            cookies = json.loads(c_str)
        except:
            return
        for c in cookies:
            jop2.cookies.set(c['name'], c['value'])

    def start_keep_get_alimama_order(self):
        t = Thread(target=self.getAlmamaOrderDetails, args=())
        t.setDaemon(True)
        t.start()

    def start_keep_get_jd_order(self):
        t = Thread(target=self.getJdOrderDetails, args=())
        t.setDaemon(True)
        t.start()

    def start_keep_get_pdd_order(self):
        t = Thread(target=self.getPddOrderDetails, args=())
        t.setDaemon(True)
        t.start()

    def getAlmamaOrderDetails(self):
        while True:
            nowtime = time.strftime('%H:%M', time.localtime(time.time()))
            if self.config.get('TIME', 'pddend') > nowtime > self.config.get('TIME', 'pddstart'):
                print('tb start .............')
                cm = ConnectMysql()
                self.load_cookies(c_tb_file, self.tb_se)
                # 获取前一天的时间
                yesterDay = str(datetime.date.today() - datetime.timedelta(days=60))
                print(yesterDay)
                getUrl = "http://pub.alimama.com/report/getTbkPaymentDetails.json?DownloadID=DOWNLOAD_REPORT_INCOME_NEW&queryType=1&payStatus=&startTime="+yesterDay+"&endTime="+str(datetime.date.today())+""

                res = self.tb_se.get(getUrl)

                fileName = 'taoBaoOrder'+yesterDay+'And'+str(datetime.date.today())+'.xls'

                if not os.path.exists('xlsx\\'+fileName+''):
                    with open('xlsx\\'+fileName+'', 'wb') as orders:
                        orders.write(res.content)

                # 把数据写入数据库
                data = xlrd.open_workbook('xlsx\\'+fileName+'')

                sheet = data.sheet_by_index(0)

                status = { '订单结算': 1, '订单付款': 2, '订单失效': 3, '订单成功': 4 }

                lists = []
                for i  in range(0, sheet.nrows):
                    if i > 0:
                        value = sheet.row_values(i)
                        is_sql = "SELECT * FROM taojin_get_orders WHERE order_id='"+value[24]+"';"
                        # 判断数据是否存在
                        is_ext = cm.ExecQuery(is_sql)
                        if is_ext == ():
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid)\
                            VALUES('"+value[24]+"', '"+value[3]+"', '"+value[2]+"', '"+str(value[7])+"', '"+str(value[6])+"', '"+str(value[12])+"', '1', '"+str(status[value[8]])+"', '"+str(value[18])+"', '"+value[0]+"', '"+value[16]+"', '"+self.bot.self.puid+"')"
                            cm.ExecNonQuery(in_sql)
                        else:
                            del_sql = "DELETE FROM taojin_get_orders WHERE order_id='"+value[24]+"';"
                            cm.ExecNonQuery(del_sql)
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid)\
                            VALUES('"+value[24]+"', '"+value[3]+"', '"+value[2]+"', '"+str(value[7])+"', '"+str(value[6])+"', '"+str(value[12])+"', '1', '"+str(status[value[8]])+"', '"+str(value[18])+"', '"+value[0]+"', '"+value[16]+"', '"+self.bot.self.puid+"')"
                            cm.ExecNonQuery(in_sql)
                        lists.append(value)

                # 获取用户的订单
                user_orders = cm.ExecQuery("SELECT * FROM taojin_order WHERE status='1' AND order_source = '1' AND bot_puid='"+self.bot.self.puid+"'  AND completion_time>'"+yesterDay+"';")
                print(user_orders)
                user_orders_id_list = []
                for item in user_orders:
                    user_orders_id_list.append(item[3])

                orders_list =[]
                for item2 in lists:
                    orders_list.append(item2[24])
                for item3 in user_orders_id_list:
                    if item3 in orders_list:
                        userOrder = cm.ExecQuery("SELECT * FROM taojin_get_orders WHERE order_id="+item3+"")
                        userOrder2 = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id="+item3+"")
                        userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder2[0][7]+"'")
                        print(item3)
                        # 根据订单状态进行回复和结算奖金
                        if userOrder[0][7] == 4 or userOrder[0][7] == 1:
                            # 已结算
                            self.changeInfoAlimama(userOrder2[0][7], userOrder[0], self.bot)
                            up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                            print(up_set_sql)
                            cm.ExecNonQuery(up_set_sql)
                        elif userOrder[0][7] == 3:
                            send_text = '''
        ---------- 订单信息 -----------
        你的订单【%s】已失效
                            ''' % (item3)
                            up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                            print(up_set_sql)
                            cm.ExecNonQuery(up_set_sql)
                            user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                            user.send(send_text)
                    else:
                        userOrder = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id="+item3+"")
                        userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder[0][7]+"'")
                        send_text = '''
        ---------订单消息----------
        抱歉你的订单【%s】返利失败！
        该订单不是通过我们的机器人购买的
                        ''' % (item3)
                        up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                        print(up_set_sql)
                        cm.ExecNonQuery(up_set_sql)
                        user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                        user.send(send_text)
                time.sleep(7200)
            else:
                print('tb time not start .......')
                time.sleep(1800)
                continue

    def getJdOrderDetails(self):

        while True:
            nowtime = time.strftime('%H:%M', time.localtime(time.time()))
            if self.config.get('TIME', 'jdend') > nowtime > self.config.get('TIME', 'jdstart'):
                print('jd start........')
                cm = ConnectMysql()
                self.jd_load_cookies(c_jd_file, self.jd_se)
                # 获取前一天的时间
                yesterDay = str(datetime.date.today() - datetime.timedelta(days=60))

                getUrl = "https://media.jd.com/rest/report/detail/in/export?accountDateStr=1%23"+yesterDay+"%23"+str(datetime.date.today())+"&orderTime=1&shortcutDate=&orderStatus=0&unionId=2011005331&unionTrafficType=0"
                res = self.jd_se.get(getUrl)

                fileName = 'jdOrder'+yesterDay+'And'+str(datetime.date.today())+'.csv'

                if not os.path.exists('xlsx\\'+fileName+''):
                    with open('xlsx\\'+fileName+'', 'wb') as orders:
                        orders.write(res.content)

                status = { ',已结算': 1, ',已付款': 2, ',无效': 3, ',无效-取消': 3, ',已完成': 4, ',代付款': 2 }
                lists = []
                # 把数据写入数据库
                with open('xlsx\\'+fileName+'') as f:
                    reader = csv.reader(f, delimiter='\t')
                    for value in reader:
                        if reader.line_num > 1:
                            is_sql = "SELECT * FROM taojin_get_orders WHERE order_id='"+value[1].split(',')[1]+"';"
                            # 判断数据是否存在
                            is_ext = cm.ExecQuery(is_sql)
                            if value[6]:
                                status_in = 5

                            status_in = status[value[8]]
                            if is_ext == ():
                                in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid)\
                                VALUES('"+value[1].split(',')[1]+"', '"+value[2].split(',')[1]+"', '"+str(value[3].split(',')[1])+"', '"+str(value[4].split(',')[1])+"', '"+str(value[5].split(',')[1])+"', '"+str(value[17].split(',')[1])+"', '2', '"+str(status_in)+"', '"+str(value[18].split(',')[1])+"', '"+value[0]+"', '"+str(value[19].split(',')[1])+"', '"+self.bot.self.puid+"')"
                                print(in_sql)
                                cm.ExecNonQuery(in_sql)
                            else:
                                del_sql = "DELETE FROM taojin_get_orders WHERE order_id='"+value[1].split(',')[1]+"';"
                                cm.ExecNonQuery(del_sql)
                                in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid)\
                                VALUES('"+value[1].split(',')[1]+"', '"+value[2].split(',')[1]+"', '"+value[3].split(',')[1]+"', '"+str(value[4].split(',')[1])+"', '"+str(value[5].split(',')[1])+"', '"+str(value[17].split(',')[1])+"', '2', '"+str(status_in)+"', '"+str(value[18].split(',')[1])+"', '"+value[0]+"', '"+str(value[19].split(',')[1])+"', '"+self.bot.self.puid+"')"
                                cm.ExecNonQuery(in_sql)
                            lists.append(value)

                # 获取用户的订单
                user_orders = cm.ExecQuery("SELECT * FROM taojin_order WHERE status='1' AND order_source = '2' AND bot_puid='"+self.bot.self.puid+"'  AND completion_time>'"+yesterDay+"';")
                user_orders_id_list = []
                for item in user_orders:
                    user_orders_id_list.append(item[3])

                orders_list =[]
                for item2 in lists:
                    orders_list.append(item2[1].split(',')[1])

                for item3 in user_orders_id_list:
                    if item3 in orders_list:
                        userOrder = cm.ExecQuery("SELECT * FROM taojin_get_orders WHERE order_id="+item3+"")
                        userOrder2 = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id="+item3+"")
                        userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder2[0][7]+"'")
                        print(item3)
                        # 根据订单状态进行回复和结算奖金
                        if userOrder[0][7] == 4 or userOrder[0][7] == 1:
                            print(userOrder)
                            # 已完成
                            self.changeInfoJd(userOrder2[0][7], userOrder[0], self.bot)
                            up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                            cm.ExecNonQuery(up_set_sql)
                            cm.Close()
                            continue
                        elif userOrder[0][7] == 3 or userOrder[0][7] == 5:
                            send_text = '''
        ---------- 订单信息 -----------
        
        订单【%s】已失效
                            ''' % (item3)
                            user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                            user.send(send_text)
                            up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                            cm.ExecNonQuery(up_set_sql)
                            cm.Close()
                            cm.Close()
                    else:
                        userOrder = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id="+item3+"")
                        userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder[0][7]+"'")
                        send_text = '''
        ---------订单消息----------
        
        订单【%s】返利失败！
        该订单不是通过当前机器人购买
                        ''' % (item3)
                        user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                        user.send(send_text)
                        up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                        cm.ExecNonQuery(up_set_sql)
                        cm.Close()
                time.sleep(7200)
            else:
                print('jd time not start .......')
                time.sleep(1800)
                continue

    def getPddOrderDetails(self):

        while True:
            nowtime = time.strftime('%H:%M', time.localtime(time.time()))
            if self.config.get('TIME', 'pddend') > nowtime > self.config.get('TIME', 'pddstart'):
                print('pdd start................')
                cm = ConnectMysql()
                self.jd_load_cookies(c_pdd_file, self.pdd_se)
                # 获取前一天的时间
                yesterDay = str(datetime.date.today() - datetime.timedelta(days=40))
                getUrl = "http://jinbao.pinduoduo.com/network/api/order/list"

                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Cache-Control':'no-cache',
                    'Connection': 'keep-alive',
                    'Content-Length': '106',
                    'Content-Type': 'application/json; charset=utf-8',
                    'Host':'jinbao.pinduoduo.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://jinbao.pinduoduo.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
                }

                data = {"startTime": str(yesterDay),"endTime": str(datetime.date.today()),"pageSize":20,"pageNum":1,"orderType":"0","timeType":"1"}
                res = self.pdd_se.post(getUrl, headers=headers, data=json.dumps(data))

                rj = json.loads(res.text)
                if rj['success']:
                    # 成功
                    data = rj['result']['list']
                    print(data)
                    status = { '已支付待成团': 2, '已成团': 2, '已收货': 1, '审核失败': 3, '审核通过': 4 }
                    # 把订单插入数据库
                    for value in data:
                        is_sql = "SELECT * FROM taojin_get_orders WHERE pdd_order_id='"+value['orderSn']+"'" \
                                                                                                         ";"
                        print(is_sql)
                        # 判断数据是否存在
                        is_ext = cm.ExecQuery(is_sql)
                        print('isiisisisisisisisisisis', is_ext)
                        status_in = status[value['orderStatusDesc']]
                        if is_ext == ():
                            if value['verifyTime']:
                                a = int(str(value['verifyTime'])[0:-3])
                                verify_time = time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(a))
                            else:
                                verify_time = ""
                            b = int(str(value['orderCreateTime'])[0:-3])

                            create_time = time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(b))
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid, pdd_order_id)\
                            VALUES('123456', '"+str(value['goodsId'])+"', '"+value['goodsName']+"', '"+str(value['goodsPrice'] / 100)+"', '"+str(value['goodsQuantity'])+"', '"+str(value['orderAmount'] / 100)+"', '3', '"+str(status_in)+"', '"+str(value['promotionAmount'] / 100)+"', '"+str(create_time)+"', '"+str(verify_time)+"', '"+self.bot.self.puid+"', '"+value['orderSn']+"')"
                            print(in_sql)
                            cm.ExecNonQuery(in_sql)
                        else:
                            del_sql = "DELETE FROM taojin_get_orders WHERE pdd_order_id='"+value['orderSn']+"';"
                            print(del_sql)
                            cm.ExecNonQuery(del_sql)
                            if value['verifyTime']:
                                a = int(str(value['verifyTime'])[0:-3])
                                verify_time = time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(a))
                            else:
                                verify_time = ""
                            b = int(str(value['orderCreateTime'])[0:-3])
                            create_time = time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(b))
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid, pdd_order_id)\
                            VALUES('123456', '"+str(value['goodsId'])+"', '"+value['goodsName']+"', '"+str(value['goodsPrice'] / 100)+"', '"+str(value['goodsQuantity'])+"', '"+str(value['orderAmount'] / 100)+"', '3', '"+str(status_in)+"', '"+str(value['promotionAmount'] / 100)+"', '"+str(create_time)+"', '"+str(verify_time)+"', '"+self.bot.self.puid+"', '"+value['orderSn']+"')"
                            print(in_sql)
                            cm.ExecNonQuery(in_sql)


                    # 获取用户的订单
                    user_orders = cm.ExecQuery("SELECT * FROM taojin_order WHERE status='1' AND order_source = '3' AND bot_puid='"+self.bot.self.puid+"'  AND completion_time>'"+yesterDay+"';")

                    get_orders_list = []
                    for item2 in data:
                        get_orders_list.append(item2['orderSn'])

                    user_orders_id_list = []
                    for item in user_orders:
                        user_orders_id_list.append(item[9])


                    for item3 in user_orders_id_list:
                        if item3 in get_orders_list:
                            print(item3)
                            userOrder = cm.ExecQuery("SELECT * FROM taojin_get_orders WHERE pdd_order_id='"+item3+"'")
                            userOrder2 = cm.ExecQuery("SELECT * FROM taojin_order WHERE pdd_order_id='"+item3+"'")
                            userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder2[0][7]+"'")
                            print(userOrder)
                            # 根据订单状态进行回复和结算奖金
                            if userOrder[0][7] == 1:
                                # 已完成
                                print(userOrder)
                                self.changeInfoPdd(userOrder2[0][7], userOrder[0], self.bot)
                            elif userOrder[0][7] == 3 or userOrder[0][7] == 5:
                                send_text = '''
            ---------- 订单信息 -----------
            你的订单【%s】已失效
                                ''' % (item3)
                                user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                                user.send(send_text)
                        else:
                            userOrder = cm.ExecQuery("SELECT * FROM taojin_order WHERE pdd_order_id='"+item3+"'")
                            print(userOrder)
                            userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+userOrder[0][7]+"'")
                            send_text = '''
            ---------订单消息----------
            抱歉你的订单【%s】返利失败！
            该订单不是通过我们的机器人购买的
                            ''' % (item3)
                            user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                            user.send(send_text)
                time.sleep(7200)
            else:
                print('pdd time not start .......')
                time.sleep(1800)
                continue

    def changeInfoAlimama(self, puid, orderInfo, bot):
        try:
            cm = ConnectMysql()
            # 查询用户是否有上线
            check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';"
            check_user_res = cm.ExecQuery(check_user_sql)
            this_user = self.bot.friends().search(nick_name=check_user_res[0][4])[0]
            # 定义SQL语句 查询用户是否已经存在邀请人
            # 判断是否已经有邀请人了
            if check_user_res and check_user_res[0][17] != '0':

                # 获取邀请人信息
                get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';"

                get_parent_info = cm.ExecQuery(get_parent_sql)

                # 计算返佣
                add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3t')), 2)
                # 累加余额
                withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                # 累加淘宝总返利
                taobao_rebate_amount = round(float(check_user_res[0][8]) + add_balance, 2)
                # 累加总返利
                total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                jishen = round(float(orderInfo[4]) * float(orderInfo[5]) - float(orderInfo[6]))

                if jishen < 0:
                    jishen = 0

                # 计算共节省金额,商品原价减去实际支付价格，加上原有节省金额加上返佣
                save_money = round(check_user_res[0][10] + jishen + add_balance, 2)
                # 总订单数加一
                total_order_num = int(check_user_res[0][11]) + 1
                # 淘宝订单数加一
                taobao_order_num = int(check_user_res[0][13]) + 1

                # 邀请人返利金额
                add_parent_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn4')), 2)

                # 给邀请人好友返利加上金额
                friends_rebatr = round(float(get_parent_info[0][19]) + float(add_parent_balance))
                # 邀请人总钱数加上返利金额
                withdrawals_amount2 = round(float(get_parent_info[0][9]) + float(add_parent_balance), 2)

                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount) + "', save_money='"+ str(save_money) +"', taobao_rebate_amount='"+ str(taobao_rebate_amount) +"', total_rebate_amount='"+ str(total_rebate_amount) +"', order_quantity='"+str(total_order_num)+"', taobao_order_quantity='"+str(taobao_order_num)+"', update_time='"+str(time.time())+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")
                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount2) + "', friends_rebate='"+str(friends_rebatr)+"', update_time='"+str(time.time())+"' WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';")

                select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                # 订单已完成，修改备注
                '''order_num = cm.ExecQuery(select_order_num)

                if order_num == ():
                    split_arr = this_user.remark_name.split('_')
                    new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE order_id='"+str(orderInfo[1])+"'")

                # 累计订单数量
                order_nums = cm.ExecQuery(select_order_num)

                split_arr2 = this_user.remark_name.split('_')

                new_remark_name2 = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name2)

                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name2+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")
                '''
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
                parent_puid = get_parent_info[0][2]
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

    您的好友【%s】又完成了一笔订单，返利提成%s元已发放到您的账户
    回复【个人信息】查询账户信息及提成
                ''' % (check_user_res[0][4], add_parent_balance)

                user_text = '''
    一一一一系统消息一一一一

    订单【%s】已完成！
    返利金%s元已发放到您的个人账户！
    回复【提现】可申请账户余额提现
    回复【个人信息】可看个当前账户信息

                ''' % (orderInfo[1], add_balance)


                cm.Close()

                parent_user = self.bot.friends().search(nick_name=get_parent_info[0][4])[0]


                parent_user.send(parent_user_text)
                this_user.send(user_text)
            else:
                add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3t')), 2)
                withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                taobao_rebate_amount = round(float(check_user_res[0][8]) + add_balance, 2)
                total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                jishen = add_balance

                if jishen < 0:
                    jishen = 0

                save_money = round(check_user_res[0][10] + jishen + add_balance, 2)
                total_order_num = int(check_user_res[0][11]) + 1
                taobao_order_num = int(check_user_res[0][13]) + 1

                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                    withdrawals_amount) + "', save_money='" + str(save_money) + "', taobao_rebate_amount='" + str(
                    taobao_rebate_amount) + "', total_rebate_amount='" + str(
                    total_rebate_amount) + "', order_quantity='"+str(total_order_num)+"', taobao_order_quantity='"+str(taobao_order_num)+"', update_time='" + str(time.time()) + "' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")

                select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                # 订单已完成，修改备注
                '''order_num = cm.ExecQuery(select_order_num)

                if order_num == ():
                    split_arr = this_user.remark_name.split('_')
                    new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    self.logger.debug(new_remark_name)
                    bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE order_id='"+str(orderInfo[1])+"'")

                # 累计订单数量
                order_nums = cm.ExecQuery(select_order_num)

                split_arr2 = this_user.remark_name.split('_')

                new_remark_name2 = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name2)

                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name2+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")'''

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

    订单【%s】已完成！
    返利金%s元已发放到您的个人账户！

    回复【提现】可申请账户余额提现
    回复【个人信息】可看个当前账户信息
                            ''' % (orderInfo[1], add_balance)
                cm.Close()

                this_user.send(user_text)

        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            return {'info': 'feild'}

    def changeInfoJd(self, puid, orderInfo, bot):
        try:
            cm = ConnectMysql()
            # 查询用户是否有上线
            check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';"
            check_user_res = cm.ExecQuery(check_user_sql)
            this_user = self.bot.friends().search(nick_name=check_user_res[0][4])[0]
            print('this_user', this_user.remark_name)
            # 判断是否已经有个人账户，没有返回信息
            if len(check_user_res) < 1:
                cm.Close()
                return {"info": "not_info"}
            else:

                # 定义SQL语句 查询用户是否已经存在邀请人
                # 判断是否已经有邀请人了
                if check_user_res and check_user_res[0][17] != '0':

                    get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';"
                    get_parent_info = cm.ExecQuery(get_parent_sql)

                    # 计算返利金额
                    add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3j')), 2)
                    # 累加宗金额
                    withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                    # 计算京东返利金额
                    jd = round(float(check_user_res[0][7]) + add_balance, 2)
                    # 计算总返利金额
                    total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                    jishen = round(float(orderInfo[4]) * float(orderInfo[5]) - float(orderInfo[6]))

                    if jishen < 0:
                        jishen = 0

                    # 计算总节省金额
                    save_money = round(
                        check_user_res[0][10] + jishen, 2)

                    add_parent_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn4')), 2)

                    withdrawals_amount2 = round(float(get_parent_info[0][9]) + add_parent_balance, 2)

                    # 订单数加1
                    # 总订单数加一
                    total_order_num = int(check_user_res[0][11]) + 1
                    # 京东订单数加一
                    jd_order_num = int(check_user_res[0][12]) + 1

                    cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount) + "', save_money='" + str(save_money) + "', jd_rebate_amount='" + str(jd) + "', total_rebate_amount='" + str(total_rebate_amount) + "', update_time='" + str(time.time()) + "', order_quantity='"+str(total_order_num)+"', jd_order_quantity='"+str(jd_order_num)+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")
                    cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount2) + "', friends_rebate='"+str(add_parent_balance)+"', update_time='" + str(time.time()) + "' WHERE lnivt_code='" + str(check_user_res[0][17]) + "';")


                    select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                    # 订单已完成，修改备注
                    # order_num = cm.ExecQuery(select_order_num)
                    #
                    # if order_num == ():
                    #     split_arr = this_user.remark_name.split('_')
                    #     new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    #     bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)
                    #
                    #     cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")
                    #
                    #
                    # cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE order_id='"+str(orderInfo[1])+"'")
                    #
                    # # 累计订单数量
                    # order_nums = cm.ExecQuery(select_order_num)
                    #
                    # split_arr2 = this_user.remark_name.split('_')
                    #
                    # new_remark_name = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))
                    #
                    # bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)
                    #
                    # cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

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

                    parent_puid = get_parent_info[0][2]
                    args2 = {
                        'wx_bot': bot.self.nick_name,
                        'bot_puid': bot.self.puid,
                        'username':get_parent_info[0][4],
                        'puid': parent_puid,
                        'rebate_amount': add_parent_balance,
                        'type': 4,
                        'create_time': time.time()
                    }


                    # 写入返利日志
                    cm.InsertRebateLog(args2)

                    parent_user_text = '''
    一一一一  推广信息 一一一一

    您的好友【%s】又完成了一笔订单，返利提成%s元已发放到您的账户
    回复【个人信息】查询账户信息及提成
                            ''' % (check_user_res[0][2], add_parent_balance)

                    user_text = '''
    一一一一系统消息一一一一

    订单【%s】已完成！
    返利金%s元已发放到您的个人账户！

    回复【提现】可申请账户余额提现
    回复【个人信息】可看个当前账户信息
                            ''' % (orderInfo[1], add_balance)


                    cm.Close()
                    parent_user = self.bot.friends().search(nick_name=get_parent_info[0][4])[0]


                    parent_user.send(parent_user_text)
                    this_user.send(user_text)
                else:
                    add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3j')), 2)
                    withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                    jd = round(float(check_user_res[0][7]) + add_balance, 2)
                    total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                    jishen = round(float(orderInfo[4]) * float(orderInfo[5]) - float(orderInfo[6]))

                    if jishen < 0:
                        jishen = 0
                    save_money = round(check_user_res[0][10] + jishen, 2)

                    # 订单数加1
                    # 总订单数加一
                    total_order_num = int(check_user_res[0][11]) + 1
                    # 京东订单数加一
                    jd_order_num = int(check_user_res[0][12]) + 1

                    up_sql = "UPDATE taojin_user_info SET jd_rebate_amount='" + str(jd) + "', withdrawals_amount='" + str(withdrawals_amount) + "', save_money='" + str(save_money) + "', total_rebate_amount='" + str(total_rebate_amount) + "', update_time='" + str(time.time()) + "', order_quantity='"+str(total_order_num)+"', jd_order_quantity='"+str(jd_order_num)+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid+"';"

                    cm.ExecNonQuery(up_sql)

                    select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                    # 订单已完成，修改备注
                    # order_num = cm.ExecQuery(select_order_num)
                    #
                    # if order_num == ():
                    #     split_arr = this_user.remark_name.split('_')
                    #     new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    #     bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)
                    #
                    #     u2 = "UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'"
                    #     cm.ExecNonQuery(u2)
                    #
                    # cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE order_id='"+str(orderInfo[1])+"'")
                    #
                    # # 累计订单数量
                    # order_nums = cm.ExecQuery(select_order_num)
                    #
                    # split_arr2 = this_user.remark_name.split('_')
                    #
                    # new_remark_name = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))
                    #
                    # bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)
                    # cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")

                    args = {
                        'wx_bot': bot.self.nick_name,
                        'bot_puid': bot.self.puid,
                        'username': check_user_res[0][4],
                        'rebate_amount': add_balance,
                        'puid': puid,
                        'type': 3,
                        'create_time': time.time()
                    }


                    # 写入返利日志
                    cm.InsertRebateLog(args)

                    user_text = '''
    一一一一 订单消息 一一一一

    订单【%s】标记成功，返利金%s已发放到您的账户
    回复【个人信息】 查看订单及返利信息

    回复【提现】可申请账户余额提现
    回复【个人信息】可看个当前账户信息
                                ''' % (orderInfo[1], add_balance)
                    cm.Close()
                    this_user.send(user_text)
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            return {'info': 'feild'}
        
    def changeInfoPdd(self, puid, orderInfo, bot):
        cm = ConnectMysql()
        try:
            # 查询用户是否有上线
            check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';"
            check_user_res = cm.ExecQuery(check_user_sql)
            this_user = self.bot.friends().search(nick_name=check_user_res[0][4])[0]
            # 定义SQL语句 查询用户是否已经存在邀请人
            # 判断是否已经有邀请人了
            if check_user_res and check_user_res[0][17] != '0':

                get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(check_user_res[0][17]) + "' AND bot_puid='"+ bot.self.puid +"';"
                get_parent_info = cm.ExecQuery(get_parent_sql)

                # 计算返利金额
                add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3j')), 2)
                # 累加宗金额
                withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                # 计算拼多多返利金额
                pdd = round(float(check_user_res[0][25]) + add_balance, 2)
                # 计算总返利金额
                total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                jishen = round(float(orderInfo[4]) * float(orderInfo[5]) - float(orderInfo[6]))

                if jishen < 0:
                    jishen = 0

                # 计算总节省金额
                save_money = round(
                    check_user_res[0][10] + jishen, 2)

                add_parent_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn4')), 2)

                withdrawals_amount2 = round(float(get_parent_info[0][9]) + add_parent_balance, 2)

                # 订单数加1
                # 总订单数加一
                total_order_num = int(check_user_res[0][11]) + 1
                # 拼多多订单数加一
                pdd_order_num = int(check_user_res[0][26]) + 1
                
                # 更新数据
                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount) + "', save_money='" + str(save_money) + "', pdd_rebate_amount='" + str(pdd) + "', total_rebate_amount='" + str(total_rebate_amount) + "', update_time='" + str(time.time()) + "', order_quantity='"+str(total_order_num)+"', pdd_order_quantity='"+str(pdd_order_num)+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid +"';")
                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(withdrawals_amount2) + "', friends_rebate='"+str(add_parent_balance)+"', update_time='" + str(time.time()) + "' WHERE lnivt_code='" + str(check_user_res[0][17]) + "';")


                select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                # 订单已完成，修改备注
                '''order_num = cm.ExecQuery(select_order_num)

                if order_num == ():
                    split_arr = this_user.remark_name.split('_')
                    new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)

                    cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")


                cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE pdd_order_id='"+orderInfo[13]+"'")

                # 累计订单数量
                order_nums = cm.ExecQuery(select_order_num)

                split_arr2 = raw.sender.remark_name.split('_')

                new_remark_name = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)

                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")
'''
                cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE pdd_order_id='" + str(orderInfo[13]) + "'")
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

                parent_puid = get_parent_info[0][2]
                args2 = {
                    'wx_bot': bot.self.nick_name,
                    'bot_puid': bot.self.puid,
                    'username':get_parent_info[0][4],
                    'puid': parent_puid,
                    'rebate_amount': add_parent_balance,
                    'type': 4,
                    'create_time': time.time()
                }


                # 写入返利日志
                cm.InsertRebateLog(args2)

                parent_user_text = '''
一一一一  推广信息 一一一一

您的好友【%s】又完成了一笔订单，返利提成%s元已发放到您的账户
回复【个人信息】查询账户信息及提成
                        ''' % (check_user_res[0][2], add_parent_balance)

                user_text = '''
一一一一系统消息一一一一

订单【%s】已完成！
返利金%s元已发放到您的个人账户！

回复【提现】可申请账户余额提现
回复【个人信息】可看个当前账户信息
                        ''' % (orderInfo[13], add_balance)
                cm.Close()
                parent_user = self.bot.friends().search(nick_name=get_parent_info[0][4])[0]


                parent_user.send(parent_user_text)
                this_user.send(user_text)
            else:
                add_balance = round(float(orderInfo[9]) * float(self.config.get('BN', 'bn3j')), 2)
                withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                pdd = round(float(check_user_res[0][7]) + add_balance, 2)
                total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                jishen = round(float(orderInfo[4]) * float(orderInfo[5]) - float(orderInfo[6]))

                if jishen < 0:
                    jishen = 0
                save_money = round(check_user_res[0][10] + jishen, 2)

                # 订单数加1
                # 总订单数加一
                total_order_num = int(check_user_res[0][11]) + 1
                # 拼多多订单数加一
                pdd_order_num = int(check_user_res[0][26]) + 1

                up_sql = "UPDATE taojin_user_info SET pdd_rebate_amount='" + str(pdd) + "', withdrawals_amount='" + str(withdrawals_amount) + "', save_money='" + str(save_money) + "', total_rebate_amount='" + str(total_rebate_amount) + "', update_time='" + str(time.time()) + "', order_quantity='"+str(total_order_num)+"', jd_order_quantity='"+str(pdd_order_num)+"' WHERE puid='" + puid + "' AND bot_puid='"+ bot.self.puid+"';"

                cm.ExecNonQuery(up_sql)

                select_order_num = "SELECT * FROM taojin_order WHERE puid='"+puid+"' AND bot_puid='"+bot.self.puid+"'"
                # 订单已完成，修改备注
                '''order_num = cm.ExecQuery(select_order_num)

                if order_num == ():
                    split_arr = this_user.remark_name.split('_')
                    new_remark_name = '%s%s%s%s%s%s%s' % (split_arr[0], '_', split_arr[1], '_', 'C', '_', split_arr[3])
                    bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)

                    u2 = "UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'"
                    cm.ExecNonQuery(u2)
                '''
                cm.ExecNonQuery("UPDATE taojin_order SET status=2 WHERE pdd_order_id='"+str(orderInfo[13])+"'")

                # 累计订单数量
                '''order_nums = cm.ExecQuery(select_order_num)

                split_arr2 = this_user.remark_name.split('_')

                new_remark_name = '%s%s%s%s%s%s%s' % (split_arr2[0], '_', split_arr2[1], '_', split_arr2[2], '_', len(order_nums))

                bot.core.set_alias(userName=this_user.user_name, alias=new_remark_name)
                cm.ExecNonQuery("UPDATE taojin_user_info SET remarkname = '"+new_remark_name+"' WHERE puid='" + puid + "' AND bot_puid='" + bot.self.puid + "'")'''

                args = {
                    'wx_bot': bot.self.nick_name,
                    'bot_puid': bot.self.puid,
                    'username': check_user_res[0][4],
                    'rebate_amount': add_balance,
                    'puid': puid,
                    'type': 3,
                    'create_time': time.time()
                }


                # 写入返利日志
                cm.InsertRebateLog(args)

                user_text = '''
一一一一 订单消息 一一一一

订单【%s】标记成功，返利金%s已发放到您的账户
回复【个人信息】 查看订单及返利信息

回复【提现】可申请账户余额提现
回复【个人信息】可看个当前账户信息
                            ''' % (orderInfo[13], add_balance)
                cm.Close()
                print(user_text)
                this_user.send(user_text)
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            return {'info': 'feild'}
