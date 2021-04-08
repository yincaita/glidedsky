"""
    js加密-1
"""
from env import Env
import js2py
import math
import time
import json

env = Env()
session = env.login()

# 生成js执行环境
context = js2py.EvalJs()
# python读取js
with open('js-obfuscation-1-test/js/sha1.js', 'r', encoding='utf-8') as f:
    context.execute(f.read())


"""
    获得参数t和sign
"""
def get_t_and_sign():
    # 需要提前定义的参数
    context.t = math.floor(time.time())
    # 需执行js代码
    js = '''
        var sign = sha1('Xr0Z-javascript-obfuscation-1' + t);
    '''
    # 执行js代码
    context.execute(js)
    return context.t, context.sign


# 定义 和
total = 0
for page_num in range(1, 1001):

    t, sign = get_t_and_sign()

    url = f'http://www.glidedsky.com/api/level/web/crawler-javascript-obfuscation-1/items?page={page_num}&t={t}&sign={sign}'

    response = session.get(url, headers=env.headers)

    # print(json.loads(response.text))
    nums = json.loads(response.text)['items']
    total += sum(nums)

    print(f"前 {page_num} 页数字和为: {total}")


print(f"结果是: {total}")
# 这个运行着就很爽了吖 (•ω•`)
