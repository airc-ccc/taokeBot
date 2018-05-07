# -*- coding: utf-8 -*-
# @Author: Qinglanhui
# @Date:   2018-04-29 17:23:01
# @Last Modified by:   Qinglanhui
# @Last Modified time: 2018-04-29 17:24:17

# 导入模块
import configparser
from bs4 import BeautifulSoup
from wxpy import *
from libs import my_utils
from libs import mediaJd
from libs import alimama
from libs import groupMessage
from libs import wx_bot
from libs import orther

config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")
# 初始化机器人，扫码登陆
bot = Bot(cache_path='peng.pkl')
bot.enable_puid('wxpy_puid.pkl')
mu = my_utils.init_logger()
fm = groupMessage.FormData()
mj = mediaJd.MediaJd()
al = alimama.Alimama(mu)
wb = wx_bot.tbAndJd()
ort = orther.Orther()


def taojin_init():
    if config.get('SYS', 'gm') == 'yes':
       fm.groupMessages(bot)

    if config.get('SYS', 'jd') == 'yes':
        print('jd..start....')
        mj.login()

    if config.get('SYS', 'tb') == 'yes':
        al.login()

# 消息回复(文本类型和分享类型消息)
@bot.register()
def text(msg):
    res = wb.check_if_is_tb_link(msg.raw, bot, msg)
    msg.reply(res)

# 消息回复(文本类型和分享类型消息) 群聊
@bot.register(Group)
def group_text(msg):
    res = wb.check_if_is_group(msg.raw, bot, msg)
    msg.reply(res)

# # 自动通过好友验证
@bot.register(msg_types = FRIENDS)
def auto_accept_friends(msg):
    # 通过好友验证
    new_friend = msg.card.accept()
    # 获取生成的备注
    ramerkName = ort.generateRemarkName(bot)
    # 修改备注
    bot.core.set_alias(userName=msg.raw['RecommendInfo']['UserName'], alias=ramerkName)
    # 获取邀请人
    soup = BeautifulSoup(msg.raw.get('Content'), 'lxml')
    msg_soup = soup.find('msg')
    # 邀请人昵称
    sourcname = msg_soup.get('sourcenickname')
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
一一一一 系统消息 一一一一

账户创建成功！0.3元奖励金已发放！

回复【个人信息】查看账户详情
分享【京东商品链接】或者【淘口令】
精准查询商品优惠券和返利信息！

优惠券使用教程：
'''+config.get('URL', 'course')+'''
免费看电影方法：
'''+config.get('URL', 'movie')+'''
邀请好友得返利说明：
'''+config.get('URL', 'lnvit')+'''
            '''
    new_friend.send(text)


if __name__ =='__main__':
    print('init......')
    taojin_init()

embed()
