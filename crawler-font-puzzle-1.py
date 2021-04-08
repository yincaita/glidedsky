from env import Env
import re
import base64
from fontTools.ttLib import TTFont
from lxml import etree
import io

# 数字-英语 映射
english_map = {
    '0': 'zero', '1': 'one', '2': 'two',
    '3': 'three', '4': 'four', '5': 'five',
    '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
}

"""
将源码中的字符串转化为真实的数字
    src_str: 如'231' --> 567  '23' --> 56  '1' --> 7
    digit_map: 源码数字 --> 真实数字 的映射 {"zero": see_num1, "one": see_num2, ...}
    返回: 真实数字
"""
def parse_srcstr_realnum(src_str, digit_map):
    # 分解出每一位字符 注意 join参数必须为字符串
    return int(''.join(str(digit_map[english_map[ch]]) for ch in src_str))


"""
获取从源码中的数字到见到的数字的映射
    返回: 当前页响应, 当前页的数字映射
"""
def get_response_and_digitmap(page):
    url = f"http://www.glidedsky.com/level/web/crawler-font-puzzle-1?page={page}"

    response = session.get(url, headers=env.headers)

    base64_str = re.search('base64,(.*?)[)]', response.text).group(1)

    # 解码(base64参数都是unicode编码后的串, 所以str先得encode), 解码针对的是base64_str编码成unicode后的bytes
    data = base64.b64decode(base64_str.encode())
    # 现在的data依旧是unicode编码的bytes类型, 转化为io流, 避免写文件过程
    fio = io.BytesIO(data)
    font = TTFont(fio)
    glyph_order = font.getGlyphOrder()
    # 数字映射 {"源码中的数字": "实际看到的数字", ...}
    digit_map = {}
    # 解析GlyphOrder中的<GlyphID id="" name=""> 并组成 {"zero": "see_num1", "one": "see_num2", ...}
    for glyph_name in glyph_order:
        digit_map[glyph_name] = str(font.getGlyphID(glyph_name) - 1)

    print('源码数字 -> 可见数字: ', digit_map)
    return digit_map, response


"""
获取当前页真实的数字和, 一次请求一页, 一页内的数字 映射不会变的
    page: 第几页数据
"""
def get_page_sum(page):
    digit_map, response = get_response_and_digitmap(page)
    # 获取每一个数字框
    html = etree.HTML(response.text)
    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

    # 每页和
    page_total = 0
    for div in div_list:
        # 一个数字串
        s = str(div.xpath('normalize-space(./text())'))
        # 分别解析, 如'231' -> 231
        page_total += parse_srcstr_realnum(s, digit_map)

    return page_total


env = Env()
env.login()
session = env.session

# 总和
total = 0
# 定义和
for page_num in range(1, 1001):
    total += get_page_sum(page_num)
    print(f'前 {page_num} 页和为 {total}')
