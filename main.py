# -*- coding: utf-8 -*-
# @Author: Qinglanhui
# @Date:   2018-04-29 17:23:01
# @Last Modified by:   Qinglanhui
# @Last Modified time: 2018-04-29 17:24:17

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
from libs import order


config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")
if config.get('SYS', 'showimage') == 'no':
    # 初始化机器人，扫码登陆
    bot = Bot(cache_path='peng.pkl', console_qr=1)
else:
    bot = Bot(cache_path='peng.pkl')
bot.enable_puid('wxpy_puid.pkl')
mu = my_utils.init_logger()
fm = groupMessage.FormData()
mj = mediaJd.MediaJd(bot)
al = alimama.Alimama(mu, bot)
wb = wx_bot.tbAndJd(bot)
ort = orther.Orther()
ord = order.Order(bot)
pdd = pingdd.Pdd(bot)

def taojin_init():
    # 根据参数，开启对应的服务
    if config.get('SYS', 'gm') == 'yes':
       fm.groupMessages(bot)

    if config.get('SYS', 'jd') == 'yes':
        print('jd..start....')
        mj.login()

    if config.get('SYS', 'tb') == 'yes':
        print('tb...start....')
        # al.login()

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
            print('PUIDIDIDIIDIDIDIDI', new_friend.puid)
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
    Hi~我是24h在线的淘小券机器人，用淘小券，免费领取任意淘宝、京东商品优惠券，好用的话记得分享给好友哦

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
            new_friend.send(text)
            livit_text = '''
---- 系统消息 ----
你成功的邀请了【%s】,
0.3元奖励金以到账
你永久获得该好友的购物返利红包提成
			''' % (new_friend.nick_name)
            print(lnivt_user.nick_name, livit_text)
            lnivt_user.send(livit_text)
    except Exception as e:
        trace = traceback.format_exc()
        print("error:{},trace:{}".format(str(e), trace))


if __name__ =='__main__':
    print('init......')
    taojin_init()

embed()
