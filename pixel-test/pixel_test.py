"""
测试图片 sprite.jpg 中数字范围
    得到数字开始的位置
"""
from PIL import Image

split = []
img = Image.open('sprite.jpg')
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
        if sum(pixels[x, y][:3]) != 255*3:
            # 当前列存在 非白色
            current_x_all_white = False
            break

    # 一列结束 若current_x_all_white还为True 那么说明当前列全为白色
    if current_x_all_white:
        # 当前列全白色, 并且上一列存在黑
        if not last_x_all_white:
            split.append(x)

    # print(f"上一列全白: {last_x_all_white}, 当前列全白: {current_x_all_white}")

    # 进行下一列之前 last_x_all_white就得根据当前列重新赋值
    last_x_all_white = current_x_all_white


# 开头插入-1 因为只记录了0的结束 没有记录开始
split.insert(0, -1)
# 赋值最后一个为图片宽度
split[len(split) - 1] = img.width

print('分隔:', split)
