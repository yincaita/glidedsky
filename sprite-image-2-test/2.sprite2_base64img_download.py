"""
    下载二维雪碧图并实现分割
"""
from env import Env
import random
import re
from PIL import Image
import base64
import io

# 调用封装的登陆环境
env = Env()
session = env.login()

"""
    获取二维雪碧图
"""
def get_sprite(url):
    # 请求源码
    response = session.get(url, headers=env.headers)

    # 正则解析base64
    base64_bytes = base64.b64decode(re.search('base64,(.*?)\"', response.text).group(1))

    # 可以不用写文件, 直接转为Image
    # with open('./sprite_img/sprite.png', 'wb') as f:
    #     f.write(base64_bytes)

    return Image.open(io.BytesIO(base64_bytes))


"""
    针对每一行的图片进行按列切割, 返回数字的最小宽限集合 如 [(1, 3), (5, 8), ...], 那么横向x 属于 [1, 3] 就是数字0的范围, 一起类推
"""
def get_gray_interval(row_image):
    interval_list = []

    # 前一列纯白 为真
    last_col_all_white = True
    # 数字开始x 和 数字结束x (2个变量不能被重复赋值0, 所以放到循环外部)
    num_start_x = 0
    num_end_x = 0

    # 遍历每一列, 每一行
    pixels = row_image.load()
    for x in range(row_image.width):
        # 当前列纯白为真
        cur_col_all_white = True
        for y in range(row_image.height):
            # 因为是灰度图片 只以 r 值代表颜色即可
            if pixels[x, y][0] != 255:
                cur_col_all_white = False

        # 一列迭代结束后
        # 如果 前一列为全白 and 当前列存在灰
        if last_col_all_white and not cur_col_all_white:
            num_start_x = x
        # 如果 前一列存在灰 and 当前列全白
        if not last_col_all_white and cur_col_all_white:
            num_end_x = x
            # 添加分段信息
            interval_list.append((num_start_x, num_end_x))

        # 下一列开始前, 重置 last_col_all_white
        last_col_all_white = cur_col_all_white

    return interval_list


"""
    切割为合理大小, 保存到train_img文件夹下, 作为训练集
"""
def slice_image(image):
    # 每一块的高
    piece_height = image.height / 10
    # 横向能平均切割, 纵向不能, 用ps横纵平均都是10份试一下就知道了
    # 先纵向平均切割10份 0~9
    for i in range(10):
        y = i * piece_height
        row_image = image.crop((0, y, image.width, y + piece_height))
        # 再对每一行的图片进行按列切割
        interval_list = get_gray_interval(row_image)
        # 遍历分隔 批量分割 保存数字图片
        for interval in interval_list:
            num_image = row_image.crop((interval[0], 0, interval[1], row_image.height))
            # 重置像素为 18*18 NEAREST: 低质量  BILINEAR: 双线性: BICUBIC: 三次样条插值  ANTIALIAS: 高质量  感觉中间两个效果好一些
            num_image = num_image.resize((18, 18), Image.ANTIALIAS)
            # 暂时随机取名 之后再手动调整为真实数字命名文件 随机区间大点 每次才会得到 每个数字都有10张图的结果, 共100张 不然文件会被覆盖
            num_image.save(f'./train_img/{random.randint(11, 100000)}.png')


"""
    切割base64格式的图片, 并保存
"""
def slice_base64_image(base64_str):
    image = Image.open(io.BytesIO(base64.b64decode(base64_str)))
    slice_image(image)


if __name__ == '__main__':
    url = 'http://www.glidedsky.com/level/web/crawler-sprite-image-2?page=5'
    image = get_sprite(url)
    # slice_image(image)

    base64_str = ''
    slice_base64_image(base64_str)
