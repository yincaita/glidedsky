"""
爬虫-验证码-1
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


class SeleniumEnv(object):

    def __init__(self):
        self.driver_path = 'D:\\driver\\89.0\\chromedriver.exe'
        self.url = 'http://www.glidedsky.com/level/web/crawler-captcha-1?page='

        self.driver = webdriver.Chrome(self.driver_path)
        # 参数10表示最长等待10秒, 参数0.5表示0.5秒检查一次规定的标签是否存在
        self.wait = WebDriverWait(self.driver, 2, 0.5)

    # 登陆
    def login(self):
        # 登陆
        self.driver.get("http://www.glidedsky.com/login")
        # 最大化窗口
        self.driver.maximize_window()
        self.driver.find_element_by_id('email').send_keys('ls1229344939@163.com')
        self.driver.find_element_by_id('password').send_keys('lovenowhyly0')
        self.driver.find_element_by_class_name('btn-primary').click()
        time.sleep(1)

    # 获取滑动按钮对象
    def get_slide_button(self):
        time.sleep(1)
        btn = self.driver.find_element_by_id('slideBlock')
        return btn

    # 获得原图和凹陷图的url元组
    def get_origin_cover_image(self):
        time.sleep(1)
        slide_bg = self.driver.find_element_by_id('slideBg')
        # 测试(链接总是为空...)
        # print('slide_bg: ', slide_bg)
        cover_url = slide_bg.get_attribute('src')
        # print('property:', cover_url)
        origin_url = cover_url.replace('img_index=1', 'img_index=0')
        # print('原来: ', origin_url)
        # print('覆盖: ', cover_url)
        return origin_url, cover_url

    # 判断2个像素点 不同返回True
    def point_diff(self, origin_pixel, cover_pixel, threshold):
        return abs(origin_pixel[0] - cover_pixel[0]) > threshold \
               and abs(origin_pixel[1] - cover_pixel[1]) > threshold \
               and abs(origin_pixel[2] - cover_pixel[2]) > threshold

    # 对比原图和凹陷图, 获取凹陷图相对相对整个图片的x偏移量
    def get_offset_cover(self):
        # 分别是原图和凹陷图的url
        origin_url, cover_url = self.get_origin_cover_image()
        # 请求
        origin_img = Image.open(io.BytesIO(requests.get(origin_url).content))
        origin_pixels = origin_img.load()
        # cover_pixels = Image.open(io.BytesIO(requests.get(cover_url).content)).load()
        cover_img = Image.open(io.BytesIO(requests.get(cover_url).content))
        cover_pixels = cover_img.load()

        width = cover_img.width
        height = cover_img.height
        # 原图是680*390 浏览器实际显示有340*195左右 最后偏移要除以2 (680/340)
        # 阈值
        threshold = 50
        # 取巧 因为观察到的结果中 凹陷图在的像素都大于了400像素
        for x in range(350, width):
            for y in range(0, height):
                # 阈值设置为50吧...  r,g,b值都相差50以上
                if self.point_diff(origin_pixels[x, y], cover_pixels[x, y], threshold):
                    # print(f'原图像素点: {origin_pixels[x, y]}, 凹陷图像素点: {cover_pixels[x, y]}')
                    return x / 2

    # 获取滑块相对整个图片的x偏移量
    def get_offset_slider(self):
        time.sleep(1)
        # self.wait.until(EC.presence_of_element_located((By.ID, 'slideBlock')))
        slide_block = self.driver.find_element_by_id('slideBlock')
        # 减2 相关说明看笔记
        slider_x = int(slide_block.location['x']) - 2
        # print(slider_x)
        return slider_x

    """
        验证码验证过程
    """
    def checkout(self, page_num):
        try:
            time.sleep(1)
            self.driver.get(self.url + str(page_num))
            # 注意！！！ 验证模块在iframe标签中
            # 哪个找不到 就在哪个前面加sleep ＞﹏＜
            time.sleep(1)
            # self.wait.until(EC.presence_of_element_located((By.ID, 'tcaptcha_iframe')))
            iframe = self.driver.find_element_by_id('tcaptcha_iframe')
            self.driver.switch_to.frame(iframe)
            # 获得滑动按钮
            slide_btn = self.get_slide_button()
            # 获取滑块相对整个图片的x偏移量
            slider_x = self.get_offset_slider()
            # 获取凹陷图相对相对整个图片的x偏移量
            cover_x = self.get_offset_cover()
            # 计算得到按钮向右按动的距离
            # print(f'cover_x: {cover_x}, slider_x: {slider_x}')
            move_x = cover_x - slider_x
            # print('move_x:', move_x)
            self.move_to_gap(slide_btn, self.get_track(move_x))

            # 用until等太久了
            success = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'show-success')))

            # 返回是否成功校验
            return success is not None
        except Exception as e:
            print(e)
            return False

    # 计算当前页数字和
    def get_total(self):
        # 切出iframe
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[0])
        div_list = self.driver.find_elements_by_xpath('//div[@class="card-body"]//div[@class="col-md-1"]')

        page_total = 0
        for div in div_list:
            page_total += int(div.text)

        return page_total

    """
       根据偏移量获取移动轨迹
       :param distance: 偏移量
       :return: 移动轨迹
    """
    def get_track(self, distance):
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.3
        # 初速度
        v = 0
        while current < distance:
            if current < mid:
                # 加速度为正5
                a = 5
            else:
                # 加速度为负3
                a = -3
            # 当前速度v1 = v0 + at
            v = v + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            if current > distance:
                track.append(distance - current + move)
                break
            # 加入轨迹
            track.append(round(move))
            # t时间后, 现在的速度
            v = v + a * t

        # print(f'track: {track}')
        return track

    """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
    """
    def move_to_gap(self, slider, track):
        ActionChains(self.driver).click_and_hold(slider).perform()

        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()

        time.sleep(random.random())
        ActionChains(self.driver).release().perform()


env = SeleniumEnv()
env.login()

total = 0
# 访问的页数
page = 967

while True:
    sign = env.checkout(page)

    # 如果验证失败
    if not sign:
        fail_count = 1
        print(f'第 {page} 页失败(1)!!!')
        # 重复操作 直到过验证
        while True:
            sign = env.checkout(page)
            if sign:
                print(f'第 {page} 页成功(n)!!!')
                break
            else:
                print(f'第 {page} 页失败(n) 又失败{fail_count}次!!!')
                fail_count += 1
                if fail_count > 3:
                    # 重启浏览器
                    env.driver.quit()
                    env = SeleniumEnv()
                    env.login()
                    fail_count = 0

    else:
        print(f'第 {page} 页成功(1)!!!')
    # 获取当前页和
    # 等数字加载完毕
    time.sleep(1)
    total += env.get_total()

    print(f'前{page}页和为 {total} ')
    page += 1
    if page == 1001:
        env.driver.quit()
        break

"""
中间总有网络原因...有时连页面都打不开 实在加载不出来, 分了多次测, 大概测了10多次吧...
我手动操作都还能一直出现 "网络恍惚了一下"/"拼图块半路丢失"  ???

[1, 272] => 948786 
怎么服务器还能 internal server error(nginx) 啊...
[273, 378) => 368900

T^T
[378, 1000] => 2,177,686

3495372

怀疑是腾讯防水墙有一定的访问限制, 建议每过100页等个10分钟再爬
"""
