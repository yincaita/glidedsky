"""
测试一列像素达到不同的阈值
"""
from PIL import Image

origin_img = Image.open('origin.jpg')
origin_pixels = origin_img.load()
cover_pixels = Image.open('cover.jpg').load()

width = origin_img.width
height = origin_img.height
for x in range(0, width):
    # 一列中不同像素点 计数
    diff_point = 0
    for y in range(0, height):
        if origin_pixels[x, y] != cover_pixels[x, y]:
            diff_point += 1
    print(f'第 {x} 列差异像素点共 {diff_point} 个')
