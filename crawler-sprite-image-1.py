"""
爬虫-雪碧图-1
"""
from env import Env
from lxml import etree
import re
from PIL import Image
import base64
import io

# 调用封装的登陆环境
env = Env()
session = env.login()


"""
生成分隔列表
    如: [-1, 8, 19, 31, 43, 54, 66, 79, 93, 104, 117]
"""
def get_split_list(style):
    split = []
    # 获取图片的尺寸
    base64_bytes = base64.b64decode(re.search('base64,(.*?)\"', style).group(1))
    fio = io.BytesIO(base64_bytes)
    img = Image.open(fio)
    # 获取像素集
    pixels = img.load()
    # 前一列上 全白
    last_x_all_white = True
    # x 表示从左到右
    for x in range(img.width):
        # 当前列全为白色
        current_x_all_white = True
        # y 表示从上到下
        for y in range(img.height):
            # print(f'{x,y}: ', pixels[x, y])
            # rgb和等于255*3, 则为白色, 不等则不为白色
            if sum(pixels[x, y][:3]) != 255 * 3:
                # 当前列存在 非白色
                current_x_all_white = False
                break

        # 一列结束 若current_x_all_white还为True 那么说明当前列全为白色
        if current_x_all_white:
            # 当前列全白色, 并且上一列存在黑
            if not last_x_all_white:
                split.append(x)

        # 进行下一列之前 last_x_all_white就得根据当前列重新赋值
        last_x_all_white = current_x_all_white

    # 开头插入-1 因为只记录了0的结束 没有记录开始
    split.insert(0, -1)
    # 赋值最后一个为图片宽度
    split[len(split) - 1] = img.width

    return split


"""
源码中通过解析style, 构建 class -> offset 
返回值结构: { "qaz": '-12', "wsx": '0', "rfv": '-12', ...}
"""
def get_clazzs_num_dict(style):
    # findall结构如下: [('qaz', '-12'), ('wsx', '0'), ('rfv': '-12') ...]
    # 使用dict构建如下字典 { "qaz": "-12", "wsx": "0", "rfv": "-12", ...}
    class_num_dict = dict(re.findall('.([0-9a-zA-Z]+) { background-position-x:(-?\\d+)px }', style))
    # 将值转为int 并取绝对值
    for _ in class_num_dict:
        class_num_dict[_] = abs(int(class_num_dict[_]))
    return class_num_dict


"""
获取每一页数字和
"""
def get_page_sum(page_num):
    url = f"http://www.glidedsky.com/level/web/crawler-sprite-image-1?page={page_num}"
    response = session.get(url, headers=env.headers)
    # 获取每一个数字框
    html = etree.HTML(response.text)
    div_list = html.xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

    # css样式表字符串
    style = html.xpath('normalize-space(//style/text())')
    # 得到 class -> offset 的字典
    class_num_dict = get_clazzs_num_dict(style)
    # 得到分隔列表
    split_list = get_split_list(style)
    # 每页和
    page_total = 0
    for div_col in div_list:
        # 一个数包含多少位
        length = len(div_col)
        num = 0
        for _ in range(0, length):
            # 如class="Fp0PceYg sprite" 应该只要Fp0PceYg
            clazz = div_col[_].attrib['class']
            clazz = clazz[:clazz.index(' ')]
            # clazz_num_dict 中, 键为class, 值为偏移
            offset = class_num_dict[clazz]
            # 获得真实数字n
            for index, split in enumerate(split_list):
                # 当offset为0 split为-1 这才能判断成功
                if offset < split:
                    n = index - 1
                    break
            num += n * pow(10, length - _ - 1)

        # 加这一个数, 每页有12个数嘛
        page_total += num

    return page_total


# 总和
total = 0
# 定义和
for page_num in range(1, 1001):
    total += get_page_sum(page_num)
    print(f'前 {page_num} 页和为: {total}')

