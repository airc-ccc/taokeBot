# -*-coding: UTF-8-*-
import os
import time
import webbrowser
from bottle import template
from flask import Flask
from flask import request
import configparser
from libs.mysql import ConnectMysql
from threading import Thread

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.conf', encoding="utf-8-sig")
bot2 = None

class FormData:
    def run(self):
        run_app()

    def async(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
        return wrapper

    # 获取群
    @async
    def groupMessages(self, bot):
        global bot2
        bot2 = bot
        time.sleep(10)
        yorn = input("是否重新选群？y/n:")
        if yorn == 'n':
            self.start_send_msg_thread()
            return
        print('start select groups.....')
        # 删除原有群聊数据
        cm = ConnectMysql()
        select_sql = "DELETE FROM taojin_group_message WHERE bot_puid='" + bot2.self.puid + "';"
        cm.ExecNonQuery(select_sql)

        group = bot2.groups()
        print(group)
        template_demo = """
<!DOCTPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <title>选择群聊</title>
    </head>
    <body>
        <div>
            <form action='/formdata'  method='post'>
                <h2>选择群聊</h2>
                <input type="hidden" name="username" value="{{ res }}" />
                <input type="hidden" name="bot_puid" value="{{ bot_puid }}" />
                <ul>
                % for item in items:
                    <li><input type="checkbox" name="{{ item.user_name }}" value="{{ item.nick_name }}" />{{ item.nick_name }}</li>
                %end
                </ul>
                <h2>输入需要群发内容:</h2>
                <textarea name="sendText" rows="3" cols="20"></textarea>
                <input type='submit' value='提交' />
            </form>
        </div>
    </body>
</html>
"""
        html = template(template_demo, items=group, res=bot2.self.nick_name, bot_puid=bot2.self.puid)
        with open('form.html', 'w', encoding='utf-8') as f:
            f.write(html)
        self.run()

    # 群发消息
    def send_group_meg(self):
        global bot2
        while True:
            time.sleep(int(config.get('TIME', 'group_sleep_time')))
            text = open('send.txt', 'r').read()
            # 获取图片
            fileArr = [c for a, b, c in os.walk('./groupFile')]
            cm = ConnectMysql()
            selectSql = "SELECT * FROM taojin_group_message WHERE bot_puid='" + bot2.self.puid + "'"
            groupInfo = cm.ExecQuery(selectSql)
            for item in groupInfo:
                time.sleep(int(config.get('TIME', 'group_send_time')))
                group = bot2.groups().search(item[3])[0]
                # 获取需要发送的图片
                if fileArr[0] != None:
                    for i in fileArr[0]:
                        image = 'groupFile/' + i
                        group.send_image(image)
                group.send(text)

    # 启动一个线程，定时发送商品信息
    def start_send_msg_thread(self):
        t = Thread(target=self.send_group_meg, args=())
        t.setDaemon(True)
        t.start()

fmm = FormData()

@app.route('/', methods=['GET', 'POST'])
def index():
    return "<h1>访问form路由</h1>"


@app.route('/form', methods=['GET', 'POST'])
def formShow():
    # 使用浏览器打开html
    html = open('form.html', 'r', encoding='utf-8')
    return html.read()


@app.route('/formdata', methods=['POST'])
def setData():
    cm = ConnectMysql()
    # 需要从request对象读取表单内容：
    formdata = request.form
    username = formdata['username']
    bot_puid = formdata['bot_puid']
    # 把需要群发的信息写入send.txt
    with open('send.txt', 'w') as fw:  # 写入
        fw.write(formdata['sendText'])
    # 把群聊信息写入数据库
    for item in formdata:
        if item != 'username' and item != 'sendText' and item != 'bot_puid':
            insert_sql = "INSERT INTO taojin_group_message(username, groupid, groupname, create_time, bot_puid) VALUES('" + username + "', '" + item + "', '" + \
                         formdata[item] + "', '" + str(time.time()) + "', '" + bot_puid + "')"
            cm.ExecNonQuery(insert_sql)
    # 执行群发任务
    fmm .start_send_msg_thread()
    return "添加成功！"


def run_app():
    webbrowser.open('http:127.0.0.1:5000/form')
    app.run()
