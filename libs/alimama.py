# encoding: utf-8

import re, datetime, time
import json
import configparser
import random
import traceback
import requests
from libs.orther import Orther
from libs.movie import SharMovie
from libs.mysql import ConnectMysql

cookie_fname = 'cookies_taobao.txt'
config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")

class Alimama:
    def __init__(self, logger, bot):
        if config.get('SYS', 'tb') == 'yes':
            self.logger = logger
            self.ort = Orther()
            self.movie = SharMovie()
            self.bot2 = bot
            self.se = requests.session()

    def getTao(self, msg):
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
            # print('!!!resj', resj)
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
            print(coupon_link)
            #print(coupon_link)
            # 如果接口返回错误信息
            if 'error_response' in coupon_link:
                tui_ur2l = 'http://tuijian.ptjob.net/www/public/index.html%23/index/' + id
                shortUr2l = self.movie.getShortUrl(tui_ur2l)
                r_text = '''
一一一一 返利信息 一一一一

亲, 宝贝已下架或非淘客宝贝！
为您推荐如下商品:
'''+shortUr2l+'''
                
                '''
                return r_text

            # print('coupon_link', coupon_link)
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
                ress = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title=' + resj[
                    'content'] + '&counp_link=' + coupon_link2['coupon_click_url'] + '&image_link=' + resj['pic_url'],
                                   headers={'Connection': 'close'})
                # 优惠券链接转淘口令
                taoken2 = json.loads(ress.text)['data']['model']

                # 更换符号
                tu11 = {0: '🗝', 1: '📲', 2: '🎵'}
                n11 = random.randint(0, 2)
                tao_token11 = taoken2.replace(taoken2[:1], tu11[n11])
                tao_token11 = tao_token11.replace(tao_token11[-1:], tu11[n11])
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
                                                        ''' % (resj['content'], resj['price'], fx2, tao_token11)
                return res_text
            # 获取优惠券金额
            coupon_price = coupon_link2['coupon_info'].split('减')[1].split('元')[0]

            ress=self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title='+resj['content']+'&counp_link='+coupon_link2['coupon_click_url']+'&image_link='+resj['pic_url'], headers={'Connection':'close'})
            # 优惠券链接转淘口令
            urlToToken = json.loads(ress.text)['data']['model']

            # 更换符号
            tu = {0: '🗝', 1: '📲', 2: '🎵'}
            n = random.randint(0, 2)
            tao_token = urlToToken.replace(urlToToken[:1], tu[n])
            tao_token = tao_token.replace(tao_token[-1:], tu[n])

            # 如果没有price
            if 'price' not in resj:
                res_text = '''
一一一一返利信息一一一一

【商品名】%s

【优惠券】%s元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                                                        ''' % (
                resj['content'], coupon_price, tao_token)
                return res_text

            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link2['max_commission_rate']),
                              2) / 100) * float(config.get('BN', 'bn3t')), 2)

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

    def getGroupTao(self, msg):
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

            res = self.se.get(
                'http://tuijian.ptjob.net/phpsdk/sdkList/taobao_wireless_share_tpwd_query.php?str=' + taokouling)
            resj = json.loads(res.text)
            # print('!!!resj', resj)
            if 'https://item.taobao.com' in resj['url']:
                potten2 = resj['url'].split('&id=')
                id = potten2[1].split('&sourceType')[0]
            else:
                potten = resj['url'].split('https://a.m.taobao.com/i')
                id = potten[1].split('.htm')[0]
            url3 = 'http://api.hitui.net/privilege?type=1&appkey=JoB3RIns&id=%s&pid=%s&session=%s' % (
            id, config.get('SYS', 'PID'), config.get('SYS', 'SESSION'))
            # print(url3)
            # 获取优惠券链接
            datares = self.se.get(url3)
            coupon_link = json.loads(datares.text)

            # 如果接口返回错误信息
            if 'error_response' in coupon_link:
                tui_ur2l = 'http://tuijian.ptjob.net/www/public/index.html%23/index/' + id
                shortUr2l = self.movie.getShortUrl(tui_ur2l)
                r_text = '''
一一一一 返利信息 一一一一

亲, 宝贝已下架或非淘客宝贝！
为您精选如下商品:
''' + shortUr2l + '''
                            '''
                return r_text

            # print('coupon_link', coupon_link)
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

 精选好券:''' + shortUrl + '''

                                             '''
                    return text

                # 普通商品转淘口令
                ress = self.se.get(
                    'http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title=' + resj[
                        'content'] + '&counp_link=' + coupon_link2['coupon_click_url'] + '&image_link=' + resj[
                        'pic_url'],
                    headers={'Connection': 'close'})
                # 优惠券链接转淘口令
                taoken2 = json.loads(ress.text)['data']['model']

                # 更换符号
                tu11 = {0: '🗝', 1: '📲', 2: '🎵'}
                n11 = random.randint(0, 2)
                tao_token11 = taoken2.replace(taoken2[:1], tu11[n11])
                tao_token11 = tao_token11.replace(tao_token11[-1:], tu11[n11])
                # 红包：券后价 * 佣金比例 / 100
                fx2 = round((round(float(resj['price']) * float(coupon_link2['max_commission_rate']), 2) / 100) * float(
                    config.get('BN', 'bn3t')), 2)
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
                                                                    ''' % (resj['content'], resj['price'], fx2, tao_token11)
                return res_text
            # 获取优惠券金额
            coupon_price = coupon_link2['coupon_info'].split('减')[1].split('元')[0]

            ress = self.se.get('http://tuijian.ptjob.net/phpsdk/sdkList/taobao_tbk_tpwd_create.php?title=' + resj[
                'content'] + '&counp_link=' + coupon_link2['coupon_click_url'] + '&image_link=' + resj['pic_url'],
                               headers={'Connection': 'close'})
            # 优惠券链接转淘口令
            urlToToken = json.loads(ress.text)['data']['model']

            # 更换符号
            tu = {0: '🗝', 1: '📲', 2: '🎵'}
            n = random.randint(0, 2)
            tao_token = urlToToken.replace(urlToToken[:1], tu[n])
            tao_token = tao_token.replace(tao_token[-1:], tu[n])

            # 如果没有price
            if 'price' not in resj:
                res_text = '''
一一一一返利信息一一一一

【商品名】%s

【优惠券】%s元
【淘链接】%s

获取返红包步骤：
1,复制本条消息打开淘宝领券
2,下完单后复制订单号发给我
                                                                    ''' % (
                    resj['content'], coupon_price, tao_token)
                return res_text

            # 红包：券后价 * 佣金比例 / 100
            fx = round((round((float(resj['price']) - int(coupon_price)) * float(coupon_link2['max_commission_rate']),
                              2) / 100) * float(config.get('BN', 'bn3t')), 2)

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

亲，当前商品暂无优惠券,建议您换一个商品试试呢。


京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                    '''
            return info

    def get_order(self, msg, orderId, userInfo, puid):

        timestr = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        order_id = int(orderId)

        cm = ConnectMysql()

        check_order_sql = "SELECT * FROM taojin_order WHERE order_id='" + str(order_id) + "' AND bot_puid = '" + self.bot2.self.puid+ "';"
        check_order_res = cm.ExecQuery(check_order_sql)

        # 判断该订单是否已经提现
        if len(check_order_res) >= 1:
            cm.Close()
            sendtext ='''
一一一一 订单消息 一一一一

订单【%s】提交成功，请勿重复提交
            ''' % (msg['Text'])
            return sendtext

        cm.ExecNonQuery("INSERT INTO taojin_order(wx_bot, username, order_id, completion_time, order_source, puid, bot_puid, status) VALUES('"+ self.bot2.self.nick_name +"', '"+str(userInfo['NickName'])+"', '"+str(order_id)+"', '" + str(timestr) + "', '1', '"+ puid +"', '"+ self.bot2.self.puid +"', '1')")

        send_text ='''
一一一一 订单消息 一一一一

订单【%s】提交成功，请耐心等待订单结算
结算成功后机器人将自动返利到您个人账户

        ''' % (order_id)
        return send_text

    def order(self, orderId, msg):
        """
        用户发送过来订单号，查询订单是否完成，完成并返利
        :param orderId:
        :return:
        """
        # 获取十分钟之前的订单
        m10 = (datetime.datetime.now()-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

        get_order_url = 'http://api.hitui.net/tbk_order?appkey=JoB3RIns&start_time={m}&span=600&session={session}&tk_status=12'\
        .format(m=m10, session=config.get('SYS', 'session'))

        print('get_order_url', get_order_url)

        response = self.se.get(get_order_url)
        print(response.text)
        adminuser = self.bot2.friends().search(config.get('ADMIN', 'ADMIN_USER'))[0]
        if 'error_response' in response.text:
            text_to_user = '''
一一一一返利信息一一一一

返利失败，可能原因：

1,订单错误请检查重新发送
2,当前订单已经失效或取消
3,当前订单并非本渠道购买
            '''

            text_to_admin = '''
一一一一返利信息一一一一

订单返利失败,订单号为{id}
用户为{user}
            '''.format(id=orderId, user=msg.sender.nick_name)

            adminuser.send(text_to_admin)
            return text_to_user

        if str(orderId) not in response.text:
            to_user = '''
一一一一返利信息一一一一

返利失败，可能原因：

1,订单错误请检查重新发送
2,当前订单已经失效或取消
3,当前订单并非本渠道购买
            '''
            return to_user

        data = json.loads(response.text)['tbk_sc_order_get_response']['results']['n_tbk_order']

        for item in data:
            if int(item['trade_id']) == int(orderId):
                # 计算返利金额
                fx = round(float(item['pub_share_pre_fee']) * float(config.get('BN', 'bn3t')), 2)
                print(fx)
                fx_pp = round(float(fx) * float(config.get('BN', 'bn4')), 2)
                try:
                    cm = ConnectMysql()
                    # 查询用户是否有上线
                    check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + msg.sender.puid + "' AND bot_puid='" + self.bot2.self.puid + "';"
                    check_user_res = cm.ExecQuery(check_user_sql)
                    # 定义SQL语句 查询用户是否已经存在邀请人
                    # 判断是否已经有邀请人了
                    if check_user_res and check_user_res[0][17] != '0':

                        # 获取邀请人信息
                        get_parent_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + str(
                            check_user_res[0][17]) + "' AND bot_puid='" + self.bot2.self.puid + "';"

                        get_parent_info = cm.ExecQuery(get_parent_sql)

                        # 计算返佣
                        add_balance = fx
                        # 累加余额
                        withdrawals_amount = round(float(check_user_res[0][9]) + add_balance, 2)
                        # 累加淘宝总返利
                        taobao_rebate_amount = round(float(check_user_res[0][8]) + add_balance, 2)
                        # 累加总返利
                        total_rebate_amount = round(float(check_user_res[0][6]) + add_balance, 2)

                        jishen = fx

                        # 计算共节省金额,商品原价减去实际支付价格，加上原有节省金额加上返佣
                        save_money = round(check_user_res[0][10] + jishen + add_balance, 2)
                        # 总订单数加一
                        total_order_num = int(check_user_res[0][11]) + 1
                        # 淘宝订单数加一
                        taobao_order_num = int(check_user_res[0][13]) + 1

                        # 邀请人返利金额
                        add_parent_balance = fx_pp

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
                            time.time()) + "' WHERE puid='" + msg.sender.puid + "' AND bot_puid='" + self.bot2.self.puid + "';")
                        cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                            withdrawals_amount2) + "', friends_rebate='" + str(friends_rebatr) + "', update_time='" + str(
                            time.time()) + "' WHERE lnivt_code='" + str(
                            check_user_res[0][17]) + "' AND bot_puid='" + self.bot2.self.puid + "';")

                        insert_to_sql = "INSERT INTO taojin_order(wx_bot, username, order_id, status, completion_time, order_source, puid, bot_puid, order_price, total_commission_rate, total_commission_fee) \
                                                VALUES ('" + self.bot2.self.nick_name + "', '" + msg.sender.nick_name + "', '" + str(
                            orderId) + "', '2','" \
                                        + item[
                                            'create_time'] + "', '2', '" + msg.sender.puid + "', '" + self.bot2.self.puid + "', '" + str(
                            item['alipay_total_price']) + "', '" + str(
                            item['total_commission_rate']) + "' , '" + fx + "')"

                        # 把订单插入数据库
                        cm.ExecNonQuery(insert_to_sql)

                        # select_order_num = "SELECT * FROM taojin_order WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "'"
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
                            'wx_bot': self.bot2.self.nick_name,
                            'bot_puid': self.bot2.self.puid,
                            'username': check_user_res[0][4],
                            'puid': msg.sender.puid,
                            'rebate_amount': add_balance,
                            'type': 3,
                            'create_time': time.time()
                        }

                        # 写入返利日志
                        cm.InsertRebateLog(args)
                        parent_puid = get_parent_info[0][2]
                        args2 = {
                            'wx_bot': self.bot2.self.nick_name,
                            'bot_puid': self.bot2.self.puid,
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
                                    ''' % (orderId, add_balance)

                        cm.Close()

                        parent_user = self.bot.friends().search(nick_name=get_parent_info[0][4])[0]

                        parent_user.send(parent_user_text)
                        return user_text
                    else:
                        add_balance = fx
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
                            time.time()) + "' WHERE puid='" + msg.sender.puid + "' AND bot_puid='" + self.bot2.self.puid + "';")

                        insert_to_sql = "INSERT INTO taojin_order(wx_bot, username, order_id, status, completion_time, order_source, puid, bot_puid, order_price, total_commission_rate, total_commission_fee) \
                        VALUES ('" + self.bot2.self.nick_name + "', '" + msg.sender.nick_name + "', '" + str(orderId) + "', '2','" \
                        + item['create_time'] + "', '2', '" + msg.sender.puid + "', '" + self.bot2.self.puid + "', '" + str(item['alipay_total_price']) + "', '" + str(item['total_commission_rate']) + "' , '" + str(fx) + "')"

                        # 把订单插入数据库
                        cm.ExecNonQuery(insert_to_sql)


                        # select_order_num = "SELECT * FROM taojin_order WHERE puid='" + puid + "' AND bot_puid='" + self.bot.self.puid + "'"
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
                            'wx_bot': self.bot2.self.nick_name,
                            'bot_puid': self.bot2.self.puid,
                            'username': check_user_res[0][4],
                            'puid': msg.sender.puid,
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
                                                ''' % (orderId, add_balance)
                        cm.Close()

                        return user_text
                except Exception as e:
                    trace = traceback.format_exc()
                    self.logger.warning("error:{},trace:{}".format(str(e), trace))
                    text_to_admin = '''
一一一一返利信息一一一一

订单返利失败,订单号为{id}
用户为{user}
                                '''.format(id=orderId, user=msg.sender.nick_name)

                    adminuser.send(text_to_admin)
                    t = '''
一一一一一 订单信息 一一一一一
订单返利失败，以联系管理员
请等待处理！
                    '''
                    return t