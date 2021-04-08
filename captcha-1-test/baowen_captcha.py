"""
测试中国保温网的滑动验证码
    http://www.cnbaowen.net/api/geetest/
"""
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import requests
import io
import time
import random
import re
import requests
from io import BytesIO

# 0.初始化selenium
driver_path = 'D:\\driver\\89.0\\chromedriver.exe'
url = 'http://www.cnbaowen.net/api/geetest/'
driver = webdriver.Chrome(driver_path)
# 参数10表示最长等待10秒, 参数0.5表示0.5秒检查一次规定的标签是否存在
wait = WebDriverWait(driver, 20, 0.5)

"""
    获得图片 图片分上下2部分, 每部分26组, 进行重组保存
    css: 图片的选择器
    name: 之后保存图片的文件名
"""
def get_image(css, name):
    # 52个div 背景图一样 但是偏移不同 根据偏移不同 重组图片并保存
    time.sleep(0.8)
    divs = driver.find_elements_by_class_name(css)
    # print(len(divs))
    # 列表装每个div背景图片的偏移
    offsets = []
    # 图片路径
    img_url = ''
    # 现在div的遍历顺序就是图片真正显示的顺序
    for div in divs:
        style = div.get_attribute('style')
        search = re.search('background-image: url\\("(.*?)"\\); background-position: (-?\\d+)px (-?\\d+)px;', style)
        img_url = search.group(1)
        x_offset = int(search.group(2))
        y_offset = int(search.group(3))

        offsets.append((x_offset, y_offset))
        # print(f'链接 {img_url}, x偏移 {x_offset}, y偏移 {y_offset}')

    # 请求图片, 根据偏移重构图片
    # img是散列排列的图片(注意: 图片全是webp格式的图片)
    img = Image.open(BytesIO(requests.get(img_url).content))
    # temp_img.save('test.jpg')  # 这时候图片还完整, 但是结果new_img结果却是黑的 说明切图/贴图出了问题

    # 第一行的26个图片
    first_line_imgs = []
    # 第二行的26个图片
    second_line_imgs = []
    # 遍历offsets, 截取原图
    for offset in offsets:
        # 当前切割的图片 10 58分别是每一块图片的宽高 (加绝对值!!!)
        x = abs(offset[0])
        y = abs(offset[1])
        cur_img = img.crop((x, y, x + 10, y + 58))
        # 说明: 原图y偏移为-58的话 现在应该填充到第一行 原图y偏移为0的话 现在应该填充到第二行
        if offset[1] == -58:
            first_line_imgs.append(cur_img)
        else:
            second_line_imgs.append(cur_img)

    # 新建空白图
    new_img = Image.new('RGB', (260, 116))
    # 填充进空白图
    # 当前填充图片的起始y坐标(0或58)
    y_now = 0
    # 填充图片的起始x坐标, 每填充一张图 就横线延展一个图片的宽(10)的距离
    x_now = 0
    for first_line_img, second_line_img in zip(first_line_imgs, second_line_imgs):
        # 一次性贴2行图片
        new_img.paste(first_line_img, (x_now, y_now))
        new_img.paste(second_line_img, (x_now, y_now + 58))
        x_now += 10

    # new_img.paste(Image.open('cover.jpg'))  # 这时候paste, new_img不存在黑像素, 说明只可能是前面切图除了问题导致贴上去的都是黑像素点(offset加绝对值!!!!)
    # 保存图片
    # new_img.save(f'./baowen/temp_img/{name}.jpg')
    # new_img.show()
    # 直接返回
    return new_img

"""
获取滑块需要向右移动的距离
    origin: 原图片 
    cover: 有凹陷, 需要验证的图片
"""
def get_move_x(origin, cover):
    origin_pixels = origin.load()
    cover_pixels = cover.load()
    width = origin.width
    height = origin.height
    for x in range(0, width):
        for y in range(0, height):
            if origin_pixels[x, y] != cover_pixels[x, y]:
                return x


"""
按照track轨迹移动slider
"""
def move_to_gap(slider, track):
    ActionChains(driver).click_and_hold(slider).perform()

    for x in track:
        ActionChains(driver).move_by_offset(x, 0).perform()

    time.sleep(0.3)
    ActionChains(driver).release(slider).perform()


"""
    横向移动的距离
    distance: 总共要走过的距离
"""
def get_track(distance):
    # 横向每一步距离
    track = []
    # 当前已经走过
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算的时间间隔
    t = 0.3
    # 初速度
    v = 0

    # 正式开始移动
    while current < distance:
        if current < mid:
            # 加速度为正
            a = 5
        else:
            a = -3

        # 移动的距离
        each_move = v * t + 1/2 * a * (t ** 2)
        # 总共移动了
        current += each_move
        # 多了 我处理为不可超出
        if current > distance:
            track.append(distance - current + each_move)
            break
        # 当前运动 计入轨迹
        track.append(round(each_move))
        # t时间后的速度
        v = v + a * t

    # print(f'轨迹如下: {track}')
    return track


def checkout():
    try:
        time.sleep(1)
        # 1.获得带缺口和不带缺口的2张图片
        # 获取不带缺口的图片
        origin_img = get_image('gt_cut_fullbg_slice', 'origin_image')
        # 获取带缺口的图片
        cover_img = get_image('gt_cut_bg_slice', 'cover_image')
        origin_img.save('./baowen/temp_img/origin.jpg')
        cover_img.save('./baowen/temp_img/cover.jpg')

        # 2.比较2张图片 像素比较 得出滑块需要右移的距离
        move_x = get_move_x(origin_img, cover_img)
        # print(f'要移动的距离 {move_x}')

        # 3.selenium模拟滑块向右滑动
        # 获取滑动按钮
        slider = driver.find_element_by_class_name('gt_slider_knob')
        move_to_gap(slider, get_track(move_x))

        success = EC.presence_of_element_located((By.CLASS_NAME, 'gt_ajax_tip gt_success'))

        return success is not None
    except Exception:
        return False


# 访问
driver.get(url)
# 最大化窗口
driver.maximize_window()
# 一个页面尝试5次
for _ in range(0, 5):
    sign = checkout()
    if sign:
        print('success')
    else:
        print('error')

    # 刷新页面
    time.sleep(1)
    driver.refresh()

driver.quit()
