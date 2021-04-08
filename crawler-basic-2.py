"""
爬虫基础2
"""
from env import Env
from lxml import etree
import re

# 调用封装的登陆环境
env = Env()
session = env.login()

# 定义 和
total = 0
# 这次需要循环遍历每一页
curr_page_url = "http://www.glidedsky.com/level/web/crawler-basic-2?page=1"
while True:
    response = session.get(curr_page_url, headers=env.headers)
    # 获取每一个数字框
    html = etree.HTML(response.text)
    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

    for div in div_list:
        total += int(div.xpath('normalize-space(./text())'))

    cur_page_num = re.search('page=(\\d+)', curr_page_url).group(1)
    print(f"前{cur_page_num}页数字和为: {total}")

    # 是否还有下一页
    next_page_btn = html.xpath('//ul[@class="pagination"]/li[last()]')[0]
    # 如果下一页按钮有disabled样式, 就没有下一页
    if next_page_btn.xpath('contains(@class, "disabled")'):
        break
    else:
        # 有下一页, 给下一页url赋值
        curr_page_url = next_page_btn.xpath('./a/@href')[0]

print(f"结果是: {total}")
