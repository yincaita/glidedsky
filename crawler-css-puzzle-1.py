"""
css反爬-1
"""
from env import Env
import re
from lxml import etree

env = Env()
env.login()
session = env.session

"""
判断一个元素是否为透明元素
    clazz: 该div的class
    style: 页面总style层叠样式表
"""
def is_opacity(clazz, style):
    opacity = re.search(clazz + ' \\{ opacity:0 \\}', style)
    return opacity is not None


"""
解析 div.col-md-1 这个div, 返回真实数据(的字符串形式)
"""
def parse_div(div, style, test_text):
    children = div.xpath('./div')
    # 伪元素选择器情况: 因为页面每个div中都是要么包含一个数字、要么为空值, 所以xpath('text()')得到的结果的列表长度无非就是 0或1, 0表示没有内容
    for index, child in enumerate(children):
        # 长度为0 说明这个div就是 <div>::before</div>
        if len(child.xpath('./text()')) == 0:
            # 从style样式表中将 child 这个div的class值对应的 content 给取出来  如: UFihK6LyIh:before { content:"240" } 将240找出
            return re.search(child.attrib['class'] + ':before \\{ content:"(\\d+)" \\}', style).group(1)

    # 接下来是孩子有3/4个的处理 注意: 在隐形元素之后出现的div元素它的index都得减去它之前隐形元素出现的个数, 才是该div的初始位置
    opacity_count = 0
    # res装最终结果 最多之支持4位数字
    res = [-1, -1, -1, -1]
    # index能记录当前div在源码中的索引
    for index, child in enumerate(children):
        # 类名
        clazz = child.attrib['class']

        # 判断当前元素是否为透明元素
        if is_opacity(clazz, style):
            opacity_count += 1
            continue

        # 非透明元素, 先看是否有position: relative
        relative = re.search(clazz + ' \\{ position:relative \\}', style)

        # 当前div的值
        val = child.xpath('./text()')[0]
        # 不存在的话定位, 就是原位置, 但是得刨去隐藏元素站的位置
        if relative is None:
            res[index - opacity_count] = val
        else:
            # 存在定位就使用当前index加上left:xem 的值, 先获取left:xem  注意search (:?)
            offset = re.search(clazz + ' \\{ left:(-?\\d)em \\}', style).group(1)
            res[index + int(offset) - opacity_count] = val

    # try:
    r = ''.join([i for i in res if i != -1])
    # except Exception as e:
    #     print(e)
    return r


"""
获取每一页数字和
"""
def get_page_sum(page_num):
    url = f"http://www.glidedsky.com/level/web/crawler-css-puzzle-1?page={page_num}"
    response = session.get(url, headers=env.headers)
    html = etree.HTML(response.text)

    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')
    # 浏览器中生成的样式
    style = html.xpath('normalize-space(//style/text())')
    # 每页和
    page_total = 0
    for div in div_list:
        # 解析div
        page_total += int(parse_div(div, style, response.text))
    return page_total


# 总和
total = 0
# 定义和
for page_num in range(1, 1001):
    total += get_page_sum(page_num)
    print(f'前 {page_num} 页和为 {total}')
