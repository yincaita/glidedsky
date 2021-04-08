import base64
from fontTools.ttLib import TTFont

# 浏览器复制base64串 保持网页不刷新 分析同一页的数据
base64_str = "浏览器源码里复制"
data = base64.b64decode(base64_str.encode())
# 现在的data依旧是unicode编码的bytes类型

# 写出为 .ttf
with open('font-puzzle-2.ttf', 'wb') as f:
    f.write(data)

# 将font-puzzle-2.ttf转为xml文件
font = TTFont('font-puzzle-2.ttf')
font.saveXML('font-puzzle-2.xml')
