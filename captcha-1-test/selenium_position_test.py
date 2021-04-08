"""
测试selenium中webelement的location是相对什么定位的
"""

from selenium import webdriver

driver = webdriver.Chrome('D:\\driver\\89.0\\chromedriver.exe')
driver.get('http://www.baidu.com/')

form = driver.find_element_by_id('form')

print(form.location)
