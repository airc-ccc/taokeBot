import time
import json
import datetime
import requests
import traceback
import configparser
from threading import Thread
from libs.mysql import ConnectMysql

'''
    新的订单接口
    不使用淘宝登陆cookie
'''

class newOrder:
    def __init__(self, bot):
        self.config = configparser.ConfigParser()
        self.config.read('config.conf', encoding="utf-8-sig")
        self.bot = bot
        self.se = requests.session()
        self.getTaobaoOrder()

    '''
        定时淘宝订单
    '''
    def start_keep_get_alimama_order(self):
        t = Thread(target=self.getTaobaoOrder, args=())
        t.setDaemon(True)
        t.start()

    '''
        获取淘宝订单    
    '''
    def getTaobaoOrder(self):
        if self.config.get('SYS', 'tb') == 'yes':
            while True:
                nowtime = time.strftime('%H:%M', time.localtime(time.time()))
                if self.config.get('TIME', 'tbend') > nowtime > self.config.get('TIME', 'tbstart'):
                    cm = ConnectMysql()

                    # 前60天的时间
                    yesterDay = datetime.date.today() - datetime.timedelta(days=60)

                    # 定义订单的几种状态，便于存储
                    status = {'订单结算': 1, '订单付款': 2, '订单失效': 3, '订单成功': 4}
                    # 请求订单接口
                    url = 'http://tuijian.ptjob.net/phpsdk/sdkList/orderGet.php?startTime=' + str(yesterDay) + '&endTime=' + str(datetime.date.today())
                    print('!!!!!!!!!!!Order Get Url is', url)
                    res = self.se.get(url)
                    # print('Get the orders', res.text)
                    # 转json
                    resj = json.loads(res.text)
                    print(len(resj))
                    # 数据存入数据库
                    for item in resj:
                        is_sql = "SELECT * FROM taojin_get_orders WHERE order_id='" + item['cate'] + "';"
                        # 判断数据是否存在
                        is_ext = cm.ExecQuery(is_sql)
                        if is_ext == ():
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid) VALUES('" + str(item['cate']) + "', '" + str(item['good_id']) + "', '" + item['good_title'] + "', '" + str(item['good_price']) + "', '" + str(item['good_num']) + "', '" + str(item['amount_pay']) + "', '1', '" + str(status[item['order_state']]) + "', '" + item['commission_percent'] + "', '" + str(item['add_time']) + "', '" + str(item['settlement_time']) + "', '" + self.bot.self.puid + "')"
                            cm.ExecNonQuery(in_sql)
                        else:
                            del_sql = "DELETE FROM taojin_get_orders WHERE order_id='" + item['cate'] + "';"
                            cm.ExecNonQuery(del_sql)
                            in_sql = "INSERT INTO taojin_get_orders(order_id, good_id, good_name, good_price, good_num, order_price, order_source, order_status, order_commission, create_time, settlement_time, bot_puid) VALUES('" + str(item['cate']) + "', '" + str(item['good_id']) + "', '" + item['good_title'] + "', '" + str(item['good_price']) + "', '" + str(item['good_num']) + "', '" + str(item['amount_pay']) + "', '1', '" + str(status[item['order_state']]) + "', '" + item['commission_percent'] + "', '" + str(item['add_time']) + "', '" + str(item['settlement_time']) + "', '" + self.bot.self.puid + "')"
                            cm.ExecNonQuery(in_sql)

                    # 获取用户的订单
                    user_orders = cm.ExecQuery("SELECT * FROM taojin_order WHERE status='1' AND order_source = '1' AND bot_puid='" + self.bot.self.puid + "'  AND completion_time>'" + str(yesterDay) + "';")
                    user_orders_id_list = []
                    for item in user_orders:
                        user_orders_id_list.append(item[3])

                    # 把获取到的订单信息收集到list里，方便操作数据
                    orders_list = []
                    for item2 in resj:
                        orders_list.append(item2['cate'])

                    # 遍历用户订单和获取到的订单对比，根据订单状态不同给用户返利或不返利
                    for item3 in user_orders_id_list:
                        if item3 in orders_list:
                            userOrder = cm.ExecQuery("SELECT * FROM taojin_get_orders WHERE order_id=" + item3 + "")
                            userOrder2 = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id=" + item3 + "")
                            userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='" + userOrder2[0][7] + "'")
                            # 根据订单状态进行回复和结算奖金
                            if userOrder[0][7] == 4 or userOrder[0][7] == 1:
                                # 已结算
                                self.changeInfoAlimama(userOrder2[0][7], userOrder[0])
                                up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                                cm.ExecNonQuery(up_set_sql)
                            elif userOrder[0][7] == 3:
                                send_text = '''
                ---------- 订单信息 -----------
            
                订单【%s】已失效
                                            ''' % (item3)
                                up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                                cm.ExecNonQuery(up_set_sql)
                                user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                                user.send(send_text)
                        else:
                            userOrder = cm.ExecQuery("SELECT * FROM taojin_order WHERE order_id=" + item3 + "")
                            userInfo = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='" + userOrder[0][7] + "'")
                            send_text = '''
                ---------订单消息----------
            
                订单【%s】返利失败
                该笔订单非通过机器人购买
                                        ''' % (item3)
                            up_set_sql = "UPDATE taojin_order SET status='2' WHERE order_id='" + str(item3) + "';"
                            cm.ExecNonQuery(up_set_sql)
                            user = self.bot.friends().search(nick_name=userInfo[0][4])[0]
                            user.send(send_text)
                    time.sleep(7200)
                else:
                    print('!!!! tb time not start, now time is %s .......' % nowtime)
                    time.sleep(1800)
                    continue

    '''
        执行返利，并修改用户信息
    '''
    def changeInfoAlimama(self, puid, orderInfo):
        try:
            cm = ConnectMysql()
            # 查询用户是否有上线
            check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "';"
            check_user_res = cm.ExecQuery(check_user_sql)
            this_user = self.bot.friends().search(nick_name=check_user_res[0][4])[0]
            # 定义SQL语句 查询用户是否已经存在邀请人
            # 判断是否已经有邀请人了
            if check_user_res and check_user_res[0][17] != '0':

                # 获取邀请人信息
                get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(
                    check_user_res[0][17]) + "' AND bot_puid='" + self.bot.self.puid + "';"

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

                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                    withdrawals_amount) + "', save_money='" + str(save_money) + "', taobao_rebate_amount='" + str(
                    taobao_rebate_amount) + "', total_rebate_amount='" + str(
                    total_rebate_amount) + "', order_quantity='" + str(
                    total_order_num) + "', taobao_order_quantity='" + str(
                    taobao_order_num) + "', update_time='" + str(
                    time.time()) + "' WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "';")
                cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                    withdrawals_amount2) + "', friends_rebate='" + str(friends_rebatr) + "', update_time='" + str(
                    time.time()) + "' WHERE lnivt_code='" + str(
                    check_user_res[0][17]) + "' AND bot_puid='" + self.bot.self.puid + "';")

                #select_order_num = "SELECT * FROM taojin_order WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "'"
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
                    'wx_bot': self.bot.self.nick_name,
                    'bot_puid': self.bot.self.puid,
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
                    'wx_bot': self.bot.self.nick_name,
                    'bot_puid': self.bot.self.puid,
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

好友【%s】又完成一笔订单
返利提成%s元已发放到个人账户
回复【个人信息】可查询账户详情
                ''' % (check_user_res[0][4], add_parent_balance)

                user_text = '''
一一一一系统消息一一一一

订单【%s】返利成功
返利金%s元已发放到个人账户
回复【个人信息】可查询账户详情
回复【提现】可申请账户余额提现
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
                    total_rebate_amount) + "', order_quantity='" + str(
                    total_order_num) + "', taobao_order_quantity='" + str(
                    taobao_order_num) + "', update_time='" + str(
                    time.time()) + "' WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "';")

                #select_order_num = "SELECT * FROM taojin_order WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "'"
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
                    'wx_bot': self.bot.self.nick_name,
                    'bot_puid': self.bot.self.puid,
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

订单【%s】返利成功
返利金%s元已发放到个人账户
回复【个人信息】可查询账户详情
回复【提现】可申请账户余额提现
                            ''' % (orderInfo[1], add_balance)
                cm.Close()

                this_user.send(user_text)

        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))
            return {'info': 'feild'}