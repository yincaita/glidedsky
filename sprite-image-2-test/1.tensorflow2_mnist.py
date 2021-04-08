"""
    tensorflow2.0实现手写汉字实现: http://blog.itpub.net/69978904/viewspace-2733646/
    保存模型: https://www.cnblogs.com/piaodoo/p/14124831.html
    测试tensorflow2实现mnist手写汉字识别
"""
import os

# 一定要放在 import tensorflow 之前才有效 = =
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow import keras
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.datasets import mnist
import numpy as np

# 加载数据集
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# 图片每个像素的数值都是在[0, 255]之间，所以归一化要除以255，数据要是浮点数，所以要添加一个小数点
train_images, test_images = train_images / 255.0, test_images / 255.0

"""
    重新创建一个model
"""
def new_model():
    # 定义模型
    # 搭建一个顺序模型，第一层先将数据展平，原始图片是28x28的灰度图，所以输入尺寸是（28，28），第二层节点数可以自己选择一个合适值，这里用128个节点，激活函数用relu
    #   第三层有多少个种类就写多少，[0, 9]一共有10个数字,所以必须写10，激活函数用softmax
    model = keras.Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])

    # 指定优化器、损失函数、评价指标
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['acc'])

    return model


"""
    已存在的model, 加载权重和偏置(方法一: 保存模型的权重和偏置)
"""
def load_weights_bias(model):
    if os.path.exists('./tensorflow2_mnist_model/weights_bias_model/checkpoint'):
        model.load_weights('./tensorflow2_mnist_model/weights_bias_model/my_model')
    else:
        print('第一次保存权重和偏置吧? 当前模型文件不存在呐! ')
        return None


"""
    保存model的权重和偏置
"""
def save_weight_bias(model):
    model.save_weights('./tensorflow2_mnist_model/weights_bias_model/my_model')


"""
    训练模型
"""
def train_model(model):
    # 训练模型
    model.fit(train_images, train_labels, epochs=1)


"""
    保存整个模型(方法二: 直接保存整个模型)
"""
def save_all_model(model):
    model.save('./tensorflow2_mnist_model/all_model/mnist_weights.h5')


"""
    加载整个模型
"""
def load_all_model():
    if os.path.exists('./tensorflow2_mnist_model/all_model/mnist_weights.h5'):
        return keras.models.load_model('./tensorflow2_mnist_model/all_model/mnist_weights.h5')
    else:
        print('第一次保存整个模型吧? 当前模型文件不存在呐! ')
        return None


model = new_model()
# 方法一: 开始
# load_weights_bias(model)
# train_model(model)
# save_weight_bias(model)
# 方法一: 结束

# 方法二: 开始
reload_model = load_all_model()
if reload_model is not None:
    model = reload_model

train_model(model)
save_all_model(model)
# 方法二: 结束


# 用测试集验证模型效果
test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
print('Test acc:', test_acc)

# 将图片输入模型，返回预测结果 (将测试集中的第一张图片输入模型)
predictions = model.predict(test_images)
print('predictions: ', predictions)
print('预测值:', np.argmax(predictions[0]))
print('真实值:', test_labels[0])
