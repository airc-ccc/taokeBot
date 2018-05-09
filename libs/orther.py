# -*-coding: UTF-8-*-

from __future__ import unicode_literals
import time
import datetime
import configparser
from libs import my_utils
from libs.mysql import ConnectMysql
from libs.movie import SharMovie

logger = my_utils.init_logger()

movie = SharMovie()
config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

class Orther(object):
    # 创建用户账户
    def create_user_info(self, raw, bot, msg, lnivt_code=0, tool=False, wxid=0, sourcname=0):
        cm = ConnectMysql()
        # try:
        if tool==False:
            res = bot.core.search_friends(userName=msg['FromUserName'])
        else:
            res = bot.core.search_friends(userName=msg['RecommendInfo']['UserName'])
        botself = bot.self

        if wxid == 0:
            wxid = raw.sender.puid


        is_ext = cm.ExecQuery("SELECT * FROM taojin_user_info WHERE puid='"+wxid+"' AND bot_puid='"+ bot.self.puid +"'")
        
        if is_ext != ():
            return
        
        if lnivt_code == 0:
            sql = "INSERT INTO taojin_user_info(wx_bot, puid, sex, nickname, lnivt_code, withdrawals_amount, lnivter, create_time, bot_puid, remarkname) VALUES('"+ bot.self.nick_name +"', '" +wxid + "', '" + str(res['Sex']) + "', '" + res['RemarkName'] + "', '" + wxid + "', '0.3', '" + str(lnivt_code) + "', '" + str(round(time.time())) + "', '"+ bot.self.puid +"', '"+ res['RemarkName'] +"');"
            cm.ExecNonQuery(sql)
            # 日志参数
            args = {
                'wx_bot': bot.self.nick_name,
                'bot_puid': botself.puid,
                'username': res['NickName'],
                'puid': wxid,
                'rebate_amount': 0.3,
                'type': 1,
                'create_time': time.time()
            }
            # 写入返利日志
            cm.InsertRebateLog(args)
            return
        else:
            lnivt_2_info = bot.core.search_friends(nickName=sourcname)

            lnivter_sql = "SELECT * FROM taojin_user_info WHERE lnivt_code='" + lnivt_code + "' AND bot_puid='"+ botself.puid +"' LIMIT 1;"
            # 获取邀请人信息
            lnivt_info = cm.ExecQuery(lnivter_sql)
            # 有邀请人时，插入用户信息，并奖励邀请人
            sql = "INSERT INTO taojin_user_info(wx_bot, puid, sex, nickname, lnivt_code, withdrawals_amount, lnivter, create_time, bot_puid, remarkname) VALUES('"+ bot.self.nick_name +"', '" + wxid + "', '" + str(res['Sex']) + "', '" + res['NickName'] + "', '" + str(wxid) + "', '0.3', '" + str(lnivt_code) + "', '" + str(round(time.time())) + "', '"+ botself.puid +"', '"+res['RemarkName']+"');"

            # 给邀请人余额加0.3元奖励
            jianli = round(float(lnivt_info[0][9]) + 0.3, 2)

            friends_num = int(lnivt_info[0][20]) + 1

            cm.ExecNonQuery("UPDATE taojin_user_info SET withdrawals_amount='" + str(
                jianli) + "', friends_number='" + str(friends_num) + "'  WHERE lnivt_code='" + lnivt_code + "' AND bot_puid='"+ botself.puid +"';")

            cm.ExecNonQuery(sql)

            # 日志参数
            args = {
                'wx_bot': bot.self.nick_name,
                'bot_puid': botself.puid,
                'username': res['NickName'],
                'puid': wxid,
                'rebate_amount': 0.3,
                'type': 1,
                'create_time': time.time()
            }

            parent_puid = self.getPuid(bot, lnivt_info[0][4])

            args2 = {
                'wx_bot': bot.self.nick_name,
                'bot_puid': botself.puid,
                'username': lnivt_info[0][4],
                'puid': parent_puid,
                'rebate_amount': 0.3,
                'type': 2,
                'create_time': time.time()
            }

            # 写入返利日志
            cm.InsertRebateLog(args)
            cm.InsertRebateLog(args2)
            lnivt_text = '''
    一一一一系统消息一一一一

    您的好友【%s】已邀请成功！

    0.3元奖励金已到账
    您将永久获得该好友永久购物返利佣金提成
            ''' % (res['NickName'])

            cm.Close()
            # 给邀请人发消息
            lnivt_user = bot.core.search_friends(userName=lnivt_2_info[0]['UserName'])
            my_friends = bot.friends().search(lnivt_user['NickName'])[0]
            my_friends.send(lnivt_text)
            return
        # except Exception as e:
        #     logger.debug(e)
        #     return e

    # 判断用户是否有个人账户
    def ishaveuserinfo(self, bot, msg, raw):
        cm = ConnectMysql()

        # 获取用户和机器人的puid
        bot_puid = self.getPuid(bot, msg['ToUserName'])
        puid = self.getPuid(bot, msg['FromUserName'])
        check_user_sql = "SELECT * FROM taojin_user_info WHERE puid='" + puid + "' AND bot_puid='"+ bot_puid +"';"
        check_user_res = cm.ExecQuery(check_user_sql)
        # 判断是否已经有个人账户，没有去创建
        if len(check_user_res) < 1:
            cm.Close()
            return {"res": "not_info"}

        return {"res": "have_info"}

    # 生成备注名称
    def generateRemarkName(self, bot):
        try:
            remarkName = ''
            # 日期 + 序号 + 状态
            year = datetime.datetime.now().year # 年
            month = datetime.datetime.now().month # 月
            day = datetime.datetime.now().day # 日

            # 获取机器人好友个数, 为序号
            f_len = len(bot.friends())

            remarkName = '%s%s%s%s%s%s%s%s%s' % (year, month, day, '_', f_len, '_', 'A', '_', 0)

            return remarkName
        except Exception as e:
            return e

    def getPuid(self, bot, name):
        res = bot.core.search_friends(userName=name)
        my_friends = bot.friends().search(res['NickName'])[0]
        return my_friends.puid
