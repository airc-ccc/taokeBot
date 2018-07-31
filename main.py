# -*- coding: utf-8 -*-
# @Author: Pengtao
# @Date:   2018-04-29 17:23:01
# @Last Modified by:   Pengtao
# @Last Modified time: 2018-07-24 11:19

# 导入模块
import configparser
import traceback
from bs4 import BeautifulSoup
from wxpy import *
from libs import pingdd
from libs import my_utils
from libs import mediaJd
from libs import alimama
from libs import groupMessage
from libs import wx_bot
from libs import orther
from libs import newOrderGet


config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")
if config.get('SYS', 'showimage') == 'no':
    # 初始化机器人，扫码登陆
    bot = Bot(cache_path='peng.pkl', console_qr=1)
else:
    bot = Bot(cache_path='peng.pkl')
bot.enable_puid('wxpy_puid.pkl')
mu = my_utils.init_logger()
mj = mediaJd.MediaJd(bot)
al = alimama.Alimama(mu, bot)
wb = wx_bot.tbAndJd(bot)
ort = orther.Orther()
pdd = pingdd.Pdd(bot)
#newOrder = newOrderGet.newOrder(bot)

def taojin_init():
    # 根据参数，开启对应的服务
    if config.get('SYS', 'gm') == 'yes':
        print('group start .......')
        fm = groupMessage.FormData()
        fm.groupMessages(bot)

    if config.get('SYS', 'jd') == 'yes':
        print('jd..start....')
        mj.login()

    # if config.get('SYS', 'tb') == 'yes':
    #     print('tb...start....')
    #     al.login()

    if config.get('SYS', 'pdd') == 'yes':
        print('pdd...start....')
        pdd.login()

# 消息回复(文本类型和分享类型消息)
@bot.register()
def text(msg):
    print(msg)
    res = wb.check_if_is_tb_link(msg.raw, bot, msg)
    msg.reply(res)

# 消息回复(文本类型和分享类型消息) 群聊
@bot.register(Group)
def group_text(msg):
    print(msg)
    if config.get('SYS', 'groupReply') == 'yes':
        res = wb.check_if_is_group(msg.raw, bot, msg)
        msg.reply(res)

# # 自动通过好友验证
@bot.register(msg_types = FRIENDS)
def auto_accept_friends(msg):
    try:
        # 获取邀请人
        soup = BeautifulSoup(msg.raw.get('Content'), 'lxml')
        msg_soup = soup.find('msg')
        # 邀请人昵称
        sourcname = msg_soup.get('sourcenickname')
        print('gsdf',sourcname)
        if sourcname:
            # 通过好友验证
            new_friend = msg.card.accept()
            # 获取生成的备注
            ramerkName = ort.generateRemarkName(bot)
            # 修改备注
            bot.core.set_alias(userName=msg.raw['RecommendInfo']['UserName'], alias=ramerkName)
            # 被邀请人puid
            user_wxid = new_friend.puid
            if sourcname == '':
                sourc = 0
            else:
                # 获取邀请人puid
                lnivt_user = bot.friends().search(sourcname)[0]
                sourc = lnivt_user.puid

            ort.create_user_info(msg, bot, msg.raw, lnivt_code=sourc, tool=True, wxid=user_wxid, sourcname=sourcname)
            text = '''
Hi~我是24h在线的淘小券机器人

    分享【京东商品】
    分享【淘口令】
    分享【拼多多商品】
    回复【帮助】查看机器人指令

    精准查询全网内部优惠券哦，您也可以访问下边优惠券商城自主查询呢！
京东优惠券商城：
'''+config.get('URL', 'jdshop')+'''
淘宝优惠券商城：
'''+config.get('URL', 'tbshop')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
                '''
            new_friend.send(text)
    except Exception as e:
        trace = traceback.format_exc()
        print("error:{},trace:{}".format(str(e), trace))


if __name__ =='__main__':
    print('init......')
    taojin_init()

embed()
