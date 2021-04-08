# encoding:utf-8
import requests
import json
import base64

# client_id 为官网获取的AK， client_secret 为官网获取的SK
# url_token = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id' \
#             '=o3fOutOOkCu7ThRaoOdQuwIW&client_secret=H8kKsreTN5WKuTXmwZZZNGL3c50bICYI'

# response = requests.get(url_token)
# 24.6ad0d52352796d8c3964fb0466ef54c8.2592000.1619511123.282335-23885544
# token = response.json()['access_token']
token = '24.6ad0d52352796d8c3964fb0466ef54c8.2592000.1619511123.282335-23885544'

# 文档: https://cloud.baidu.com/doc/OCR/s/vk3h7y58v
ocrnum_url = f'https://aip.baidubce.com/rest/2.0/ocr/v1/general'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

with open('sprite.jpg', 'rb') as f:
    img = base64.b64encode(f.read())

params = {
    "language_type": "ENG",
    "access_token": token,
    "image": img
}

response = requests.post(ocrnum_url, headers=headers, data=params)
print(response.json())

res_list = response.json()['words_result']

for line in res_list:
    print(line['words'])
