"""
    雪碧图2 - 训练数据测试
"""
import os

# 一定要放在 import tensorflow 之前才有效 = =
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Flatten, Dense
import numpy as np
from PIL import Image
import random

model_path = './glided_sky_model/glided_sky_model.h5'

"""
    获取图片训练数据, 并转化为mnist类似的数据结构
"""
def get_train_data_like_mnist(train_img_path, other_paths):
    filepath_list = [os.path.join(train_img_path, _) for _ in os.listdir(train_img_path)]

    for other_path in other_paths:
        filepath_list.extend([os.path.join(other_path, _) for _ in os.listdir(other_path)])


    # 训练时文件名列表一定要shuffle一下!!! 测试不存在
    random.shuffle(filepath_list)

    # 初始化
    images = np.zeros([len(filepath_list), 18, 18])
    labels = np.zeros(len(filepath_list))

    # 遍历每个文件
    for index, filepath in enumerate(filepath_list):
        image = Image.open(filepath)
        # 遍历每个图片的所有像素点
        print(index)
        width = image.width
        height = image.height
        for x in range(0, width):
            for y in range(0, height):
                # 单通道取 r值 即可  构建[b, 18, 18]  保证灰度值在 0~1
                images[index][x][y] = image.getpixel((x, y))[0] / 255.0

        # 遍历完一个文件, 才赋值labels
        # 取label 文件名切片 最后一个 / 之后的的第一个字母 就是label
        last_index = filepath.rfind('/') + 1
        labels[index] = filepath[last_index: last_index + 1]

    return tf.convert_to_tensor(images, dtype=tf.float32), tf.convert_to_tensor(labels, dtype=tf.int32)


def new_model():
    # 定义模型
    # 搭建一个顺序模型，第一层先将数据展平，原始图片是18x18灰度图，所以输入尺寸是（18，18），第二层节点数可以自己选择一个合适值，这里用128个节点，激活函数用relu
    #   第三层有多少个种类就写多少，[0, 9]一共有10个数字,所以必须写10，激活函数用softmax
    model = keras.Sequential([
        Flatten(input_shape=(18, 18)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])

    # 指定优化器、损失函数、评价指标
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['acc'])

    return model


def train_model(model, train_images, train_labels, epoch):
    # 训练模型
    model.fit(train_images, train_labels, epochs=epoch)


def save_model(model):
    model.save(model_path)


# 加载模型
def load_model():
    if os.path.exists(model_path):
        return keras.models.load_model(model_path)
    else:
        print('第一次保存整个模型吧? 当前模型文件不存在呐! ')
        return None


if __name__ == '__main__':
    # 之前手动检测的数据集
    # images, labels = get_train_data_like_mnist('./train_img_old/')

    # 知道单页连续请求后的新数据集目录
    images, labels = get_train_data_like_mnist('./train_img_new/', ('./train_img_new_add1/', './train_img_new_add2/', './train_img_new_add3/'))
    # images, labels = get_train_data_like_mnist('./train_img_new_add1/')
    # images, labels = get_train_data_like_mnist('./train_img_new_add2/')
    # images, labels = get_train_data_like_mnist('./train_img_new_add3/')

    model = new_model()

    # 加载存储的模型
    reload_model = load_model()
    if reload_model is not None:
        model = reload_model

    # 训练模型 epoch训练次数
    train_model(model, images, labels, 50)
    save_model(model)

    # images_test, labels_test = get_train_data_like_mnist('./temp/')
    # 用测试集验证模型效果
    # loss, accuracy = model.evaluate(images_test, labels_test, verbose=2)
    # print('test accuracy:', accuracy)

    # 将图片输入模型，返回预测结果
    # predictions = model.predict(images_test)
    # print('predictions: ', predictions)
    # for i in range(0, len(predictions)):
    #     print('预测值:', np.argmax(predictions[i]), '  真实值:', int(labels_test[i]), bool(labels_test[i] == np.argmax(predictions[i])))
    # print('test accuracy:', accuracy)

