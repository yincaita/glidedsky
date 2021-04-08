import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.90 Safari/537.36 "
}

proxies = {
    "http": "106.14.198.6:8080"
}

# url = "http://www.baidu.com"
# 测试代理生效
url = "http://httpbin.org/get"

response = requests.get(url, headers=headers, proxies=proxies)

print(json.loads(response.text)["origin"])
