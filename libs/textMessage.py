# -*-coding: UTF-8-*-

import time
import traceback
import re
import configparser
from urllib.parse import quote
from libs.mysql import ConnectMysql
from libs.orther import Orther
from libs import mediaJd
from libs import alimama
from libs import my_utils
from libs import tuling
from libs import movie


config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")

class TextMessage:
    def __init__(self, bot):
        self.tu = tuling.tuling()
        self.mjd = mediaJd.MediaJd(bot)
        self.logger = my_utils.init_logger()
        self.al = alimama.Alimama(self.logger, bot)
        self.ort = Orther()
        self.movie = movie.SharMovie()

    def is_valid_date(self, str):
        try:
            time.strptime(str, "%Y-%m-%d")
            return True
        except:
            return False

    def getText(self, raw, bot, msg):
        wei_info = bot.core.search_friends(userName=msg['FromUserName'])
        patternURL = re.compile('^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+')

        pattern_bz = re.compile('^帮助$')
        pattern_profile = re.compile('^个人信息$')
        pattern_tixian = re.compile('^提现$')
        pattern_tuig = re.compile('^推广$')
        pattern_proxy = re.compile('^代理$')
        appect_friend = re.compile('^我通过了你的朋友验证请求，现在我们可以开始聊天了$')
        # 判断是否是URL链接
        if patternURL.search(msg['Text']) == None:

            pattern_s = re.compile('^搜')
            pattern_z = re.compile('^找')
            pattern_m = re.compile('^买')
            if (pattern_s.search(msg['Text']) != None) | (pattern_z.search(msg['Text']) != None) | (
                    pattern_m.search(msg['Text']) != None):

                res = self.ort.ishaveuserinfo(bot, msg, raw)

                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                jdurl = quote("http://jdyhq.ptjob.net/?r=search?kw=" + msg['Text'][1:], safe='/:?=&')

                tburl = quote('http://taoquan.ptjob.net/index.php?r=l&kw=' + msg['Text'][1:], safe='/:?=&')

                res1 = self.movie.getShortUrl(jdurl)
                res2 = self.movie.getShortUrl(tburl)
                text = '''
一一一一系统消息一一一一
亲，以下是【%s】优惠券集合

京东：%s
淘宝：%s
                ''' % (msg['Text'][1:], res1, res2)
                return text
            elif appect_friend.search(msg['Text']) != None:
                # 获取生成的备注
                ramerkName = self.ort.generateRemarkName(bot)
                self.logger.debug(ramerkName)
                # 修改备注
                bot.core.set_alias(userName=msg['FromUserName'], alias=ramerkName)
                # 被邀请人puid
                user_wxid = self.ort.getPuid(bot, msg['FromUserName'])
                self.ort.create_user_info(raw, bot, msg, lnivt_code=0, tool=True, wxid=user_wxid)
                text = '''
Hi~我是24h在线的淘小券机器人，用淘小券，免费领取任意淘宝、京东，拼多多商品优惠券，好用的话记得分享给好友哦

回复【帮助】可查询指信息

分享
【京东商品链接】
【拼多多商品链接】
【淘口令】查询商品优惠券
分享【VIP视频链接】免费查看高清VIP视频！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                        '''
                return text
            elif ('你已添加了' in msg['Text']) and ('现在可以开始聊天了' in msg['Text']):
                arrstr = msg['Text'].split('，')
                str = arrstr[0][5:]
                self.logger.debug(str)
                user = bot.friends().search(str)[0]
                self.logger.debug(str, user)
                # 获取生成的备注
                ramerkName = self.ort.generateRemarkName(bot)
                self.logger.debug(ramerkName)
                # 修改备注
                bot.core.set_alias(nickName=user.user_name, alias=ramerkName)
                # 被邀请人puid
                user_wxid = user.puid
                self.ort.create_user_info(raw, bot, msg, lnivt_code=0, tool=True, wxid=user_wxid)
                text = '''
Hi~我是24h在线的淘小券机器人，用淘小券，免费领取任意淘宝、京东，拼多多商品优惠券，好用的话记得分享给好友哦

回复【帮助】可查询指信息

分享
【京东商品链接】
【拼多多商品链接】
【淘口令】查询商品优惠券
分享【VIP视频链接】免费查看高清VIP视频！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                        '''
                return text
            elif pattern_bz.search(msg['Text']) != None:
                res = self.ort.ishaveuserinfo(bot, msg, raw)

                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                # 帮助操作
                text = '''
Hi~我是24h在线的淘小券机器人，用淘小券，免费领取任意淘宝、京东，拼多多商品优惠券，好用的话记得分享给好友哦

回复【帮助】可查询指信息

分享
【京东商品链接】
【拼多多商品链接】
【淘口令】查询商品优惠券
分享【VIP视频链接】免费查看高清VIP视频！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                        '''
                return text
            elif pattern_tixian.search(msg['Text']) != None:
                cm = ConnectMysql()
                res = self.ort.ishaveuserinfo(bot, msg, raw)

                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                print(config.get('ADMIN', 'ADMIN_USER'))
                adminuser = bot.friends().search(config.get('ADMIN', 'ADMIN_USER'))[0]
                print(adminuser)
                # try:
                select_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + raw.sender.puid + "' AND bot_puid='"+ bot.self.puid+"';"
                select_user_res = cm.ExecQuery(select_user_sql)
                timestr = round(time.time())
                timestr2 = repr(timestr)
                if float(select_user_res[0][9]) > 0:
                    # 修改余额
                    update_sql = "UPDATE taojin_user_info SET withdrawals_amount='0', update_time='"+ timestr2 +"' WHERE puid='"+raw.sender.puid+"' AND bot_puid='"+ bot.self.puid +"';"
                    print(update_sql)
                    total_amount = float(select_user_res[0][6]) + float(select_user_res[0][9])
                    update_total_sql = "UPDATE taojin_user_info SET total_rebate_amount='" + repr(total_amount) + "',update_time='" + timestr2 + "' WHERE puid='"+raw.sender.puid +"' AND bot_puid='"+ bot.self.puid +"';"
                    # 插入提现日志
                    insert_current_log_sql = "INSERT INTO taojin_current_log(wx_bot, username, amount, create_time, puid, bot_puid) VALUES('" + bot.self.nick_name +"', '" + wei_info['NickName'] + "', '" + repr(select_user_res[0][9]) + "', '" + timestr2 + "', '"+ raw.sender.puid +"', '"+bot.self.puid+"')"
                    print(insert_current_log_sql)
                    to_admin_text = '''
一一一一 提现通知 一一一一

机器人：%s
提现人：%s
提现金额：%s 元
提现时间：%s
                                        ''' % (
                    bot.self.nick_name, wei_info['NickName'], select_user_res[0][9],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                    cm.ExecNonQuery(update_sql)
                    cm.ExecNonQuery(update_total_sql)
                    cm.ExecNonQuery(insert_current_log_sql)

                    to_user_text = '''
一一一一 提现信息 一一一一

提现成功！
提现金额将以微信红包的形式发放，请耐心等待！

分享【京东商品链接】或者【淘口令】
精准查询商品优惠券和返利信息！
                                    '''
                    print(to_user_text)
                    adminuser.send(to_admin_text)
                    return to_user_text
                else:
                    text2 = '''
一一一一 提现信息 一一一一

提现申请失败，账户余额为0！
                                    '''
                    return text2
                # except Exception as e:
                #     trace = traceback.format_exc()
                #     print("error:{},trace:{}  京东登录失效 正在重新登录京东".format(str(e), trace))
                #     text1 = '''
# 一一一一 系统信息 一一一一
#
# 提现失败，请稍后重试！
#                             '''
#                     return text1
            elif pattern_profile.search(msg['Text']) != None:
                cm = ConnectMysql()
                res = self.ort.ishaveuserinfo(bot, msg, raw)
                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                user_sql = "SELECT * FROM taojin_user_info WHERE puid='" +raw.sender.puid + "' AND bot_puid='"+ bot.self.puid +"';"

                user_info = cm.ExecQuery(user_sql)

                current = "SELECT sum(amount) FROM taojin_current_log WHERE puid='" +raw.sender.puid + "' AND bot_puid='"+ bot.self.puid +"';"

                current_info = cm.ExecQuery(current)

                # 如果总提现金额不存在，赋值为0
                if current_info[0][0] == None:
                    current_info = 0
                else:
                    current_info = current_info[0][0]
                print(user_info, current_info)
                text = '''
一一一一 个人信息 一一一一

总返利金额: %s元
京东返利金额: %s元
淘宝返利金额: %s元
可提现余额: %s元
累计提现金额: %s元

累计订单量: %s
京东订单量: %s
淘宝订单量: %s
总好友返利: %s
总好友个数: %s
                                    ''' % (user_info[0][6], user_info[0][7], user_info[0][8], user_info[0][9], current_info, user_info[0][11],user_info[0][12], user_info[0][13], user_info[0][19], user_info[0][20])
                cm.Close()
                return text
            elif pattern_tuig.search(msg['Text']) != None:
                cm = ConnectMysql()
                res = self.ort.ishaveuserinfo(bot, msg, raw)

                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + raw.sender.puid + "' AND bot_puid='"+ bot.self.puid +"';"

                cm.ExecQuery(user_sql)

                text = '''
一一一一 推广信息 一一一一

将机器人名片分享到群或者好友
好友添加机器人为好友
您和好友都将获取'''+ config.get('BN', 'bn2') +'''元现金奖励
您将永久享受好友返利提成
邀请好友得返利：
'''+config.get('URL', 'lnvit')+'''
                                '''
                return text
            elif pattern_proxy.search(msg['Text']) != None:
                res = self.ort.ishaveuserinfo(bot, msg, raw)

                if res['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)
                text = '''
一一一一系统消息一一一一

您好！
点击链接：'''+config.get('URL', 'proxy')+'''
添加好友备注：跑堂优惠券代理

客服人员将尽快和您取得联系，请耐心等待!
                        '''
                return text
            elif (',' in msg['Text']) and (msg['Text'].split(',')[1].isdigit()) and (len(msg['Text'].split(',')[1]) == 11):

                res2 = self.ort.ishaveuserinfo(bot, msg, raw)

                if res2['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                res = self.mjd.get_jd_order(bot, msg, msg['Text'].split(',')[0], msg['Text'].split(',')[1], wei_info, raw.sender.puid, raw)

                if res['info'] == 'success':
                    parent = bot.friends().search(res['parent'])
                    parent.send(res['parent_user_text'])
                    return res['user_text']
                elif res['info'] == 'order_exit':
                    return res['send_text']
                elif res['info'] == 'not_order':
                    return res['user_text']
                elif res['info'] == 'not_parent_and_success':
                    return res['user_text']
                elif res['info'] == 'feild':

                    user_text = '''
一一一一订单信息一一一一

订单返利失败！

失败原因：
【1】未确认收货（打开App确认收货后重新发送）
【2】当前商品不是通过机器人购买
【3】查询格式不正确(正确格式：2018-03-20,73462222028 )
【4】订单完成日期错误，请输入正确的订单查询日期
【6】订单号错误，请输入正确的订单号

请按照提示进行重新操作！
                                        '''
                    return user_text
            elif ('，' in msg['Text']) and (msg['Text'].split('，')[1].isdigit()) and (
                    len(msg['Text'].split('，')[1]) == 11):
                res2 = self.ort.ishaveuserinfo(bot, msg, raw)

                if res2['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                res = self.mjd.get_jd_order(bot, msg, msg['Text'].split('，')[0], msg['Text'].split('，')[1], wei_info, raw.sender.puid, raw)

                if res['info'] == 'success':
                    parent = bot.friends().search(res['parent'])
                    parent.send(res['parent_user_text'])
                    return res['user_text']
                elif res['info'] == 'order_exit':
                    return res['send_text']
                elif res['info'] == 'not_order':
                    return res['user_text']
                elif res['info'] == 'not_parent_and_success':
                    return res['user_text']
                elif res['info'] == 'feild':

                    user_text = '''
一一一一订单信息一一一一

订单返利失败！

失败原因：
【1】未确认收货（打开App确认收货后重新发送）
【2】当前商品不是通过机器人购买
【3】查询格式不正确(正确格式：2018-03-20,73462222028 )
【4】订单完成日期错误，请输入正确的订单查询日期
【6】订单号错误，请输入正确的订单号

请按照提示进行重新操作！
                                        '''
                    return user_text
            elif (',' in msg['Text']) and (msg['Text'].split(',')[1].isdigit()) and (
                    len(msg['Text'].split(',')[1]) == 18):
                res2 = self.ort.ishaveuserinfo(bot, msg, raw)
                print(res2)
                if res2['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                res = self.al.get_order(bot, msg, msg['Text'].split(',')[0], msg['Text'].split(',')[1], wei_info, raw.sender.puid, raw)

                if res['info'] == 'success':
                    parent = bot.friends().search(res['parent'])
                    parent.send(res['parent_user_text'])
                    return res['user_text']
                elif res['info'] == 'order_exit':
                    return res['send_text']
                elif res['info'] == 'not_order':
                    return res['user_text']
                elif res['info'] == 'not_parent_and_success':
                    return res['user_text']
                elif res['info'] == 'feild':
                    user_text = '''
一一一一订单信息一一一一

订单返利失败！

失败原因：
【1】未确认收货（打开App确认收货后重新发送）
【2】当前商品不是通过机器人购买
【3】查询格式不正确(正确格式：2018-03-20,73462222028 )
【4】订单完成日期错误，请输入正确的订单查询日期
【6】订单号错误，请输入正确的订单号

请按照提示进行重新操作！
                                        '''

                    return user_text
            elif ('，' in msg['Text']) and (msg['Text'].split('，')[1].isdigit()) and (
                    len(msg['Text'].split('，')[1]) == 18):
                res2 = self.ort.ishaveuserinfo(bot, msg, raw)

                if res2['res'] == 'not_info':
                    self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                res = self.al.get_order(bot, msg, msg['Text'].split('，')[0], msg['Text'].split('，')[1], wei_info, raw.sender.puid, raw)

                if res['info'] == 'success':
                    parent = bot.friends().search(res['parent'])
                    parent.send(res['parent_user_text'])
                    return res['user_text']
                elif res['info'] == 'order_exit':
                    return res['send_text']
                elif res['info'] == 'not_order':
                    return res['user_text']
                elif res['info'] == 'not_parent_and_success':
                    return res['user_text']
                elif res['info'] == 'feild':
                    user_text = '''
一一一一订单信息一一一一

订单返利失败！

失败原因：
【1】未确认收货（打开App确认收货后重新发送）
【2】当前商品不是通过机器人购买
【3】查询格式不正确(正确格式：2018-03-20,73462222028 )
【4】订单完成日期错误，请输入正确的订单查询日期
【6】订单号错误，请输入正确的订单号

请按照提示进行重新操作！
                                        '''

                    return user_text
            elif (',' in msg['Text']) and (self.is_valid_date(msg['Text'].split(',')[0])):
                user_text = '''
一一一一系统消息一一一一

查询失败！信息格式有误！
正确格式如下：
订单完成时间+逗号+订单号
(京东订单号长度11位，淘宝订单号长度18位)
例如：
2018-03-03,123456765432

请确认修改后重新发送
                                        '''
                return user_text
            elif ('，' in msg['Text']) and (self.is_valid_date(msg['Text'].split('，')[0])):
                user_text = '''
一一一一系统消息一一一一

查询失败！信息格式有误！
正确格式如下：
订单完成时间+逗号+订单号
(京东订单号长度11位，淘宝订单号长度18位)
例如：
2018-03-03,123456765432

请确认修改后重新发送
                                        '''
                return user_text
            else:
                if config.get('SYS', 'tl') == 'yes':
                    msg_text = self.tu.tuling(msg)
                    self.logger.debug(msg_text)
                    return msg_text
                else:
                    return
        else:
            res2 = self.ort.ishaveuserinfo(bot, msg, raw)

            if res2['res'] == 'not_info':
                self.ort.create_user_info(raw, bot, msg, 0, tool=False)

                self.mjd.getJd(raw, bot, msg, msg['Text'])

    def getGroupText(self, bot, msg):
        patternURL = re.compile('^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+')

        pattern_bz = re.compile('^帮助$')
        pattern_tuig = re.compile('^推广$')
        pattern_proxy = re.compile('^代理$')

        # 判断是否是URL链接
        if patternURL.search(msg['Text']) == None:

            pattern_s = re.compile('^搜')
            pattern_z = re.compile('^找')
            pattern_m = re.compile('^买')
            if (pattern_s.search(msg['Text']) != None) | (pattern_z.search(msg['Text']) != None) | (
                    pattern_m.search(msg['Text']) != None):

                jdurl = quote("http://jdyhq.ptjob.net/?r=search?kw=" + msg['Text'][1:], safe='/:?=&')

                tburl = quote('http://taoquan.ptjob.net/index.php?r=l&kw=' + msg['Text'][1:], safe='/:?=&')
                res1 = self.movie.getShortUrl(jdurl)
                res2 = self.movie.getShortUrl(tburl)
                text = '''
一一一一系统消息一一一一

亲，以下是【%s】优惠券集合

京东：%s
淘宝：%s
                                ''' % (msg['Text'][1:], res1, res2)
                return text
            elif pattern_bz.search(msg['Text']) != None:
                # 帮助操作
                text = '''
一一一一 系统信息 一一一一

回复【帮助】可查询指信息
回复【提现】申请账户余额提现
回复【推广】可申请机器人代理
回复【个人信息】可看个当前账户信息

回复【买+商品名称】
回复【找+商品名称】
回复【搜+商品名称】查看商品优惠券合集

分享【京东商品链接】或者【淘口令】
精准查询商品优惠券和返利信息！
分享【VIP视频链接】免费查看高清VIP视频！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
跑堂优惠券常见问题：
'''+config.get('URL', 'faq')+'''
免费看电影方法：
'''+config.get('URL', 'movie')+'''
京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                        '''
                return text
            elif pattern_tuig.search(msg['Text']) != None:
                text = '''
一一一一 推广信息 一一一一

将机器人名片分享到群或者好友
好友添加机器人为好友
您和好友都将获取'''+ config.get('BN', 'bn2') +'''元现金奖励
您将永久享受好友返利提成
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                                '''
                return text
            elif pattern_proxy.search(msg['Text']) != None:
                text = '''
一一一一系统消息一一一一

您好！
点击链接：'''+config.get('URL', 'proxy')+'''
添加好友备注：跑堂优惠券代理

客服人员将尽快和您取得联系，请耐心等待！
                        '''
                return text
            else:
                return
        else:
            self.mjd.getGroupJd(bot, msg, msg['Text'])
