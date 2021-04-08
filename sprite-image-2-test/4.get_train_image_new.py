"""
    https://www.cnblogs.com/TurboWay/p/13678074.html
    正确的获取训练/测试数据集方式
"""
from env import Env
import re
from PIL import Image
import base64
import io
from lxml import etree
import uuid

# 调用封装的登陆环境
env = Env()
session = env.login()


"""
    获取二维雪碧图
"""
def get_sprite(response):

    # 正则解析base64
    base64_bytes = base64.b64decode(re.search('base64,(.*?)\"', response.text).group(1))
    return Image.open(io.BytesIO(base64_bytes))


"""
    以每个数字的宽高和偏移为基准切割图片 并 resize 并 保存
    num_divs: 每一个div.col-md-1 一页共12个
    image: 二维雪碧图
    style: 页面的style标签内容
    left_to_right_nums: 一页中从左到右的 single_bit_num 集合
"""
def slice_image_save(num_divs, image, style, left_to_right_nums):
    count = 0
    # 遍历div
    for num_div in num_divs:
        # 遍历每一位数字(遍历的顺序就是 left_to_right_nums 的顺序)
        for single_bit_num_div in num_div:
            # 获取样式
            clazz = single_bit_num_div.attrib['class']
            clazz = clazz[:clazz.index(' ')]
            # 从style查询 offset-x offset-y width height
            offset_x = abs(int(re.search(clazz + ' \\{ background-position-x:(-?\\d+)px', style).group(1)))
            offset_y = abs(int(re.search(clazz + ' \\{ background-position-y:(-?\\d+)px', style).group(1)))
            width = abs(int(re.search(clazz + ' \\{ width:(\\d+)px', style).group(1)))
            height = abs(int(re.search(clazz + ' \\{ height:(\\d+)px', style).group(1)))

            # 切割 雪碧图中这个偏移和宽高对应的图片 就是当前数字的图
            single_bit_num_image = image.crop((offset_x, offset_y, offset_x + width, offset_y + height))
            # resize 一定要重新赋值a 下载完了...才发现全是原尺寸...
            single_bit_num_image = single_bit_num_image.resize((18, 18), Image.ANTIALIAS)

            # 获取训练集
            # single_bit_num_image.save(f'./train_img_new/{left_to_right_nums[count]}_{uuid.uuid4().hex}.png')
            # 获取测试集
            single_bit_num_image.save(f'./test_img_new/{left_to_right_nums[count]}_{uuid.uuid4().hex}.png')
            # 10 0000 感觉还不够 再补充一些
            # single_bit_num_image.save(f'./train_img_new_add1/{left_to_right_nums[count]}_{uuid.uuid4().hex}.png')
            # single_bit_num_image.save(f'./train_img_new_add2/{left_to_right_nums[count]}_{uuid.uuid4().hex}.png')
            # single_bit_num_image.save(f'./train_img_new_add3/{left_to_right_nums[count]}_{uuid.uuid4().hex}.png')

            # 记录一次分割
            count += 1


if __name__ == '__main__':
    url = 'http://www.glidedsky.com/level/web/crawler-sprite-image-2?page=1'

    # 第一页的数字是固定的(确保每一个数字都存在) 第一页有35个单数字
    left_to_right_nums = list('33737926314413128538136429117711094')

    # 重复请求第一页
    for i in range(2900):
        print(f'------------------------------- 第 {i + 1} 次 -------------------------------')
        # 请求源码
        response = session.get(url, headers=env.headers)
        # 获取雪碧图
        sprite_image = get_sprite(response)
        # 切割和保存训练集
        html = etree.HTML(response.text)
        num_divs = html.xpath('//div[@class="col-md-1"]')
        slice_image_save(num_divs, sprite_image, html.xpath('//style/text()')[0], left_to_right_nums)

