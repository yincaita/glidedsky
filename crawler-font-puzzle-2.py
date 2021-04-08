from env import Env
import re
import base64
from fontTools.ttLib import TTFont
from lxml import etree
import io


"""
将源码中的汉字转化为真实的数字
    src_str: 如'随成成' --> 211
    uni_map: 源码汉字 --> 真实数字 的映射 {"成": 1, "随": 2, ...}
    返回: 真实数字
"""
def parse_srcstr_realnum(src_str, uni_map):
    arr = []
    for ch in src_str:
        # 每个ch都是一个汉字, 将汉字转为unicode编码, 去除串首的\u即为需要的编码
        uni = ch.encode('unicode-escape').decode()
        code = uni.replace('\\u', '')
        arr.append(uni_map[code])

    return int(''.join(arr))

"""
获取从源码中的汉字到见到的数字的映射
    返回: 当前页响应, name(unicode去除'uni')->真实数字 的映射 如, (response, {'7bd9': '0', '9716': '1', ...})
"""
def get_response_and_unimap(page):
    url = f"http://www.glidedsky.com/level/web/crawler-font-puzzle-2?page={page}"

    response = session.get(url, headers=env.headers)

    base64_str = re.search('base64,(.*?)[)]', response.text).group(1)

    # 解码(base64参数都是unicode编码后的串, 所以str先得encode), 解码针对的是base64_str编码成unicode后的bytes
    data = base64.b64decode(base64_str.encode())

    # 现在的data依旧是unicode编码的bytes类型, 转化为io流, 避免写文件过程
    fio = io.BytesIO(data)
    font = TTFont(fio)
    glyph_order = font.getGlyphOrder()
    # cmap的结构 { code: name, ... }  注意: cmap中的code是10进制
    cmap = font.getBestCmap()
    name_id_map = {}
    # 解析GlyphOrder中的<GlyphID id="" name=""> 并组成 { "name": "id-1"... }
    for glyph_name in glyph_order:
        # 现在还只是 name: id 映射
        name_id_map[glyph_name] = str(font.getGlyphID(glyph_name) - 1)
    # 定义 code_id_map {code: id, ...}
    code_id_map = {}
    # 遍历cmap, 得到 code_ip_map {code: id}
    for code in cmap:
        # 将code转化为16进制
        code_id_map[hex(code).replace('0x', '')] = name_id_map[cmap[code]]

    print('源码汉字unicode码 -> 可见数字: ', code_id_map)
    return code_id_map, response


"""
获取当前页真实的数字和, 一次请求一页, 一页内的数字 映射不会变的
    page: 第几页数据
"""
def get_page_sum(page):
    uni_map, response = get_response_and_unimap(page)
    # 获取每一个数字框
    html = etree.HTML(response.text)
    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

    # 每页和
    page_total = 0
    for div in div_list:
        # 一个数字串
        s = str(div.xpath('normalize-space(./text())'))
        # 分别解析, 如'231' -> 231
        page_total += parse_srcstr_realnum(s, uni_map)

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
