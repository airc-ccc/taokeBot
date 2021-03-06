# -*-coding: UTF-8-*-

import pymysql
import configparser

config = configparser.ConfigParser()
config.read('config.conf',encoding="utf-8-sig")

host = config.get('DB', 'DB_HOST')
user = config.get('DB', 'DB_USERNAME')
pwd = config.get('DB', 'DB_PASSWORD')
db = config.get('DB', 'DB_DATABASE')


class ConnectMysql:
    def __init__(self):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

        self._conn = self.GetConnect()
        if (self._conn):
            self._cur = self._conn.cursor()


    # 连接数据库
    def GetConnect(self):
        conn = False
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                database=self.db,
                charset="utf8"
            )
        except Exception as e:
            print("连接数据库失败, %s" % e)
        else:
            return conn

    # 执行查询
    def ExecQuery(self, sql):
        res = ""
        try:
            self._cur.execute(sql)
            res = self._cur.fetchall()
        except Exception as err:
            print("查询失败, %s" % err)
        else:
            return res

    # 执行非查询类语句
    def ExecNonQuery(self, sql):
        flag = False
        try:
            self._cur.execute(sql)
            self._conn.commit()
            flag = True
        except Exception as err:
            flag = False
            self._conn.rollback()
            print("执行失败, %s" % err)
        else:
            return flag

    # 执行非查询类语句, 事务版
    def InsertM(self, sql):
        flag = False
        try:
            self._cur.execute(sql)
            flag = True
        except Exception as err:
            flag = False
            print("执行失败, %s" % err)
        else:
            return flag

    # 获取连接信息
    def GetConnectInfo(self):
        print("连接信息：")
        print("服务器:%s , 用户名:%s , 数据库:%s " % (self.host, self.user, self.db))

    def InsertRebateLog(self,args):
        flag = False
        try:
            sql = "INSERT INTO taojin_rebate_log(wx_bot, bot_puid, username, rebate_amount, type, create_time, puid) VALUES('"+str(args['wx_bot'])+"', '"+ args['bot_puid'] +"', '"+str(args['username'])+"','"+str(args['rebate_amount'])+"','"+str(args['type'])+"','"+str(args['create_time'])+"', '"+ args['puid'] +"')"
            self._cur.execute(sql)
            flag = True
        except Exception as err:
            flag = False
            print("执行失败, %s" % err)
        else:
            return flag

    # 关闭数据库连接
    def Close(self):
        if (self._conn):
            try:
                if (type(self._cur) == 'object'):
                    self._cur.close()
                if (type(self._conn) == 'object'):
                    self._conn.close()
            except:
                raise ("关闭异常, %s,%s" % (type(self._cur), type(self._conn)))

    def CommitMysql(self):
        self._conn.commit()

    def Rollback(self):
        self._conn.rollback()
