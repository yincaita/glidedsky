"""
关于转码
    https://blog.csdn.net/yishengzhiai005/article/details/80045042
    python2中进行Base64编码和解码
    python3不太一样：因为3.x中字符都为unicode编码，而b64encode函数的参数为byte类型，所以必须先转码。

测试base64转ttf、分析ttf、xml文件
"""
from env import Env
import re
import base64
from fontTools.ttLib import TTFont

env = Env()
env.login()
session = env.session

url = "http://www.glidedsky.com/level/web/crawler-font-puzzle-1"

response = session.get(url, headers=env.headers)

# base64_str = re.search('base64,(.*?)[)]', response.text).group(1)

# 打印base64 说明每次的base64都有不同之处
# print(base64_str)
# 解码(base64参数都是unicode编码后的串, 所以str先得encode), 解码针对的是base64_str编码成unicode后的bytes

# 直接用我们无痕浏览器复制下来的base64串
base64_str = "***自己补全***"
data = base64.b64decode(base64_str.encode())
# 现在的data依旧是unicode编码的bytes类型

# 写出为 .ttf
with open('font-puzzle-1.ttf', 'wb') as f:
    f.write(data)

# 将font-puzzle-1.ttf转为xml文件
font = TTFont('font-puzzle-1.ttf')
font.saveXML('font-puzzle-1.xml')
