"""
爬虫基础1
"""
from env import Env
from lxml import etree

# 调用封装的登陆环境
env = Env()
session = env.login()

# 有了token, cookie等信息, 就能访问爬虫一页面了
url = "http://www.glidedsky.com/level/web/crawler-basic-1"
response = session.get(url, headers=env.headers)
# 获取每一个数字框
html = etree.HTML(response.text)
div_list = html.xpath('//div[@class="col-md-1"]')
# 定义 和
total = 0
for div in div_list:
    total += int(div.xpath('normalize-space(./text())'))

print(f"结果是: {total}")
