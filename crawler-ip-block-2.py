"""
ip反爬2
    和ip反爬1一样的 改下url就行
"""
from env import Env
from lxml import etree

# 调用封装的登陆环境
env = Env()
session = env.login()

# 定义 和
total = 0

# 当前页
curr_page = 1

# 代理ip的索引, 因为每1秒只能获取最多200个ip
proxy_index = 0

# 200个代理ip列表
proxy_list = env.get_proxy()

while True:
    # 这里采用代理 超时设置为0.6s 设置小一点 那么慢的代理ip就自动跳过了 但是又不能太小 毕竟代理比正常访问慢 跑完估计也得5-8分钟左右
    # 如果报错/返回403页面就用下一个代理 注意代理的 键是http 写成大写代理无效
    try:
        response = session.get(f"http://www.glidedsky.com/level/web/crawler-ip-block-2?page={curr_page}",
                               headers=env.headers, timeout=0.4, proxies={"http": proxy_list[proxy_index]})
        # 页面响应403 则也应算错误
        if 403 == response.status_code:
            raise Exception(f"该代理已经用过: {proxy_list[proxy_index]}")
    except Exception as e:
        # 直接使用下一个的proxy
        proxy_index += 1
        if proxy_index >= env.ip_each:
            proxy_list = env.get_proxy()
            # *****
            proxy_index = 0
        continue

    # 获取每一个数字框
    html = etree.HTML(response.text)
    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

    print("-"*40)
    for div in div_list:
        total += int(div.xpath('normalize-space(./text())'))

    print(f"前{curr_page}页数字和为: {total}")
    if curr_page >= 1000:
        break
    curr_page += 1

print(f"结果是: {total}")
