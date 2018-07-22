import requests
import datetime

'''
    新的订单接口
    不使用淘宝登陆cookie
'''

class newOrder:
    def __init__(self):
        pass

    '''
        获取淘宝订单    
    '''
    def getTaobaoOrder(self):
        # 请求订单接口
        url = 'http://tuijian.ptjob.net/phpsdk/sdkList/orderGet.php?startTime=' + str(datetime.date.today() - datetime.timedelta(days=60)) + 'endTime=' + str(datetime.date.today())
        print(url)
        res = requests.get(url)
