"""
环境设置
"""
import requests
import re


class Env(object):
    # 每秒获取个数 最多200 但是靠后的因为时间关系 多少会速度差些
    ip_each = 30
    # 请求数据
    login_data = {
        "email": "ls1229344939@163.com",
        "password": "密码",
        "_token": ""
    }
    # api的url
    proxy_api_url = "获取代理的api的url" + str(ip_each)

    def __init__(self):
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.90 Safari/537.36 "
        }
        # login_url
        self.login_url = "http://www.glidedsky.com/login"
        # 使用session, 自动保存登陆后获取的cookie
        self.session = requests.session()

    # 登陆获取 _token值
    def login(self):
        response = self.session.get(self.login_url, headers=self.headers)
        # 正则解析, 将_token值返回
        self.login_data["_token"] = re.search('name="_token" value="(.*?)"', response.text).group(1)
        # 登陆数据齐备, 正式登陆
        self.session.post(self.login_url, data=self.login_data, headers=self.headers)
        # print(self.login_data["_token"])
        return self.session

    """
        实时获取代理ip: 某宝找的1块测试, 1s最多获取200次api 这里获取60 感觉前面的速度快些
        ['ip1:port1', 'ip2:port2']
        过期后用的自己找的ip代理商 几块钱10000个 ip数量计费
    """
    def get_proxy(self):
        response = requests.get(self.proxy_api_url, self.headers)
        return response.text.split("\r\n")

if __name__ == '__main__':
    env = Env()
    # env.login()

    print(env.get_proxy())
