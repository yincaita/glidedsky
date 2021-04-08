"""
    https://blog.csdn.net/yishengzhiai005/article/details/80045042
    python2中进行Base64编码和解码
    python3不太一样：因为3.x中字符都为unicode编码，而b64encode函数的参数为byte类型，所以必须先转码。
"""
# 导入 base64模块
import base64

# 给定需要转换的字符串
str1 = "你好a"

# 需要转成2进制格式才可以转换，所以我们这里再手动转换一下
result = base64.b64encode(str1.encode())

# 打印转换后的结果
print('转换后的结果 -->', result)

# 再把加密后的结果解码
temp = base64.b64decode(result)

# 同样的，解码后的结0果是二进制，我们再转换一下
print('解密后的结果 --> ', temp.decode())
