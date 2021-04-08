from env import Env
from lxml import etree

env = Env()
env.login()
session = env.session
# 测试代理ip有效性
response = session.get("http://www.glidedsky.com/level/web/crawler-ip-block-2?page=1",
                       headers=env.headers, proxies={"http": "27.153.4.224:32012"})
text = response.text
print(text)
print(etree.HTML(text).xpath('//ul[@class="pagination"]/li[last()]/a/@href'))
