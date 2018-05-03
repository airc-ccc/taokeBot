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
mu = my_utils.init_logger()
fm = groupMessage.FormData()
mj = mediaJd.MediaJd()
al = alimama.Alimama(mu)
wb = wx_bot.tbAndJd()
ort = orther.Orther()


# 初始化登录京东 淘宝，和开启群发
def taojin_init():
    if config.get('SYS', 'gm') == 'yes':
       fm.groupMessages()

    if config.get('SYS', 'jd') == 'yes':
        mj.login()

    if config.get('SYS', 'tb') == 'yes':
        al.login()

# 消息回复(文本类型和分享类型消息)
@bot.register()
def text(msg):
    print(msg)
    wb.check_if_is_tb_link(msg.raw)

# 消息回复(文本类型和分享类型消息) 群聊
@bot.register(Group)
def group_text(msg):
    print(msg)
    wb.check_if_is_group(msg.raw)

# # 自动通过好友验证
@bot.register(msg_types = FRIENDS)
def auto_accept_friends(msg):
    # 接受好友请求
    print(msg)
    new_friend = msg.card.accept()
    print(new_friend)
    soup = BeautifulSoup(msg.raw.get('Content'), 'lxml')
    msg_soup = soup.find('msg')
    sourc = msg_soup.get('sourceusername')
    sourcname = msg_soup.get('sourcenickname')
    user_wxid = msg_soup.get('fromusername')
    if sourc == '':
        sourc = 0

    ort.create_user_info(msg.raw, lnivt_code=sourc, tool=True, wxid=user_wxid, sourcname=sourcname)
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

embed()

if __name__ == 'main':
    taojin_init()
