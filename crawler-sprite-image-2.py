"""
爬虫-雪碧图-2
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from env import Env
from lxml import etree
import re
from PIL import Image
import base64
import io
import numpy as np
from tensorflow import keras
import tensorflow as tf

# 调用封装的登陆环境
env = Env()
session = env.login()


"""
    获取二维雪碧图(同 2.sprite2_base64img_download.py)
    context: 网页源码
"""
def get_sprite(context):
    # 正则解析base64
    base64_bytes = base64.b64decode(re.search('base64,(.*?)\"', context).group(1))

    # 可以不用写文件, 直接转为Image
    # with open('./sprite_img/sprite.png', 'wb') as f:
    #     f.write(base64_bytes)

    return Image.open(io.BytesIO(base64_bytes))


"""
    针对每一行的图片进行按列切割, 返回数字的最小宽限集合 如 [(1, 3), (5, 8), ...], 那么横向x 属于 [1, 3] 就是数字0的范围, 一起类推
    (同 2.sprite2_base64img_download.py)
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
    将图片列表转为类似mnist数据结构的数据, 方便模型进行预测
    return: [100*18*18] 三维矩阵Tensor
        基本同 3.sprite2_train_test.py 中的 def get_train_data_like_mnist(train_img_path)
"""
def parse_images_like_mnist_data(small_images):
    # 准备三维矩阵
    images = np.zeros([len(small_images), 18, 18])

    # 遍历每个像素点
    for index, small_image in enumerate(small_images):
        # 遍历每个图片的所有像素点
        width = 18
        height = 18
        for x in range(0, width):
            for y in range(0, height):
                # 单通道取 r值 即可  构建[b, 18, 20]  保证灰度值在 0~1
                images[index][x][y] = small_image.getpixel((x, y))[0] / 255.0

    # 返回训练数据时, 需要将数据封装为Tensor
    return tf.convert_to_tensor(images, dtype=tf.float32)


"""
    预测数字
    return: 返回数字列表(str形式, 后期方便拼接)
"""
def predict(small_images, model):
    # num表示每一页数据 就是12个
    num_list = []

    images_data = parse_images_like_mnist_data(small_images)
    # 进行预测 predictions 是预测的概率值
    predictions = model.predict(images_data)

    # 预测值填充进 num_list
    for i in range(0, len(small_images)):
        # 将int64转为int
        num_list.append(np.argmax(predictions[i]))

    return num_list


"""
    根据每个单数字div的偏移和宽高从雪碧图中切割出小图, 利用模型识别数字
    image: 二位雪碧图
    context: 网页源码
    return: (切割好的 single_bit_image集合, 一页共12个数每个数有几位数字)
"""
def slice_image(image, context):
    # 每一位数字的集合
    single_bit_images = []
    # 记录总共12个数字 每个数字各有多少位
    count_bit = []

    # 获取装有数字的div
    html = etree.HTML(context)
    num_divs = html.xpath('//div[@class="col-md-1"]')
    # 获取css
    style = html.xpath('//style/text()')[0]

    # 遍历div(一整个数字)
    for num_div in num_divs:
        # 记录这个数字有多少位
        count = 0
        # 遍历每一位数字的每一位
        for single_bit_div in num_div:
            # 获取样式

            clazz = single_bit_div.attrib['class']
            clazz = clazz[:clazz.index(' ')]
            # 从style查询 offset-x offset-y width height
            offset_x = abs(int(re.search(clazz + ' \\{ background-position-x:(-?\\d+)px', style).group(1)))
            offset_y = abs(int(re.search(clazz + ' \\{ background-position-y:(-?\\d+)px', style).group(1)))
            width = abs(int(re.search(clazz + ' \\{ width:(\\d+)px', style).group(1)))
            height = abs(int(re.search(clazz + ' \\{ height:(\\d+)px', style).group(1)))

            # 切割 雪碧图中这个偏移和宽高对应的图片 就是当前数字的图
            single_bit_image = image.crop((offset_x, offset_y, offset_x + width, offset_y + height))

            # resize
            single_bit_image = single_bit_image.resize((18, 18), Image.ANTIALIAS)

            # 加入单位数字
            single_bit_images.append(single_bit_image)
            count += 1

        # 记录下这个数字的位数
        count_bit.append(count)

    return single_bit_images, count_bit


"""
    根据每一个小数字 和 每个大数字占的位数 的到大数字集合
"""
def mix_num(single_num_list, count_bit):
    index = 0
    # 结果
    num_list = []

    for bit in count_bit:
        num = 0
        # 按照位数 顺序拼接每一位 循环次数是bit次
        while bit:
            num += single_num_list[index] * (10 ** (bit - 1))
            index += 1
            bit -= 1

        # 填入
        num_list.append(num)

    return num_list


"""
    请求返回当前页数字集合
"""
def get_num_list(page_num, model):
    url = f'http://www.glidedsky.com/level/web/crawler-sprite-image-2?page={page_num}'

    response = session.get(url, headers=env.headers)

    # 一张 2维雪碧图
    sprite_image = get_sprite(response.text)
    # 分割成的 18*18 小图
    single_bit_images, count_bit = slice_image(sprite_image, response.text)

    # 推测雪碧图中的真实数字 得到数字列表
    num_list = predict(single_bit_images, model)

    # 根据列表和有几位数字获得真实数字集合
    num_list = mix_num(num_list, count_bit)
    # print(f'第 {page_num} 页的每个数字: ', num_list)

    return num_list


"""
    判断预测是否精确
"""
def is_accurate(predicts):
    # = =, 模型判断率挺高的了(都42w训练集了), 同一页请求的前三次都相同直接就返回了(即判定准确结果都还有错) 难道存在连续3次都判错的可能?
    # if len(predicts) < 3:
    if len(predicts) < 6:
        return False

    predicts_set = set(predicts)
    # 看预测结果出现的频率 认定出现频率 >= 2/3 那么这个数才是准确的(因为本身模型确认率虽然接近100% 但不是100%)
    # 统计 { 数字: 出现的次数 }
    statistics = {num: predicts.count(num) for num in predicts_set}

    # 值逆序排列 返回列表 一对键值混合为元组
    statistics = sorted(statistics.items(), key=lambda x: x[1], reverse=True)
    # 值最大的元组 的第二个元素 才是 频数, 元组第一个是数字和
    # 不用这个条件了 = =, 太多预测错误的就会一直卡在当前页了 永远达不到这个比例
    # if statistics[0][1] / len(predicts) >= 3 / 4:

    # 采用 只有频率1出现 or 频率top1 / top2 > n 我觉得4够高了啊
    if len(statistics) == 1 or statistics[0][1] / statistics[1][1] > 4:
        print(statistics)
        return statistics[0][0]
    else:
        return False


if __name__ == '__main__':
    total = 0

    # 模型文件路径
    model_path = './sprite-image-2-test/glided_sky_model/glided_sky_model.h5'
    # 加载模型(放到函数里加载报WARNING, 解决不了: ARNING:tensorflow:6 out of the last 11 calls to <function
    #       Model.make_predict_function.)
    restored_model = keras.models.load_model(model_path)

    for i in range(1, 1001):
        # 当前页的预测值集合
        predicts = []

        print('-' * 100)
        # 结果是否准确
        accurate = is_accurate(predicts)
        count = 0
        while not accurate:
            count += 1
            # 不精确 就重新请求
            num_list = get_num_list(i, restored_model)
            predicts.append(sum(num_list))
            accurate = is_accurate(predicts)

        print(f'经过 {count} 轮计算, 结果才精确!!!')
        # 判断数值是否精确 这里accurate是int64的, 源于用模型预测时 np.argmax() 结果是 int64
        print(f'第 {i} 页数据为: {num_list}, 求和是 {accurate}')

        total += accurate
        print(f'前 {i} 页, 数字和为 {total}')
        print('-' * 100)

"""
    page1 [337, 379, 263, 144, 131, 285, 381, 364, 291, 171, 110, 94]
    page1 + page2 + page3 = 2956 + 2907 + 2844 = 8707
    
    错误答案1: 2725233
    错误答案2: 2724715
    还真是出错出在连续三次都判定为错误答案!!! 修改为6次以上才判定就好了(多判定几组数据) (正确答案: )
    之前还怀疑训练42w组数据都能出错 (*￣▽￣*)
"""
