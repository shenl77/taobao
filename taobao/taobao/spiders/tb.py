# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request
from scrapy.conf import settings
import re
from bs4 import BeautifulSoup
from taobao.items import TaobaoItem
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['www.taobao.com']
    start_urls = ['http://www.taobao.com/']
    DEPTH = settings['DEPTH']
    KEYWORD = settings['KEYWORD']
    cookie=settings['COOKIE']

    def getTaobaoCookies(self):
        brower = webdriver.Chrome()
        wait = WebDriverWait(brower, 10)
        url = "https://www.taobao.com/"
        brower.get("https://login.taobao.com/member/login.jhtml")
        while True:
            print("Please login in taobao.com!")
            time.sleep(5)
            if brower.current_url == url:
                tbCookies = brower.get_cookies()
                brower.quit()
                break
        cookie = [item["name"] + ":" + item["value"] for item in tbCookies]
        cookMap = {}
        for elem in cookie:
            str = elem.split(':')
            cookMap[str[0]] = str[1]
        return cookMap

    def start_requests(self):
        cookie = self.getTaobaoCookies()
        for i in range(self.DEPTH):
            url = 'https://s.taobao.com/search?q=' + self.KEYWORD + '&s=' + str(44 * i)
            yield Request(url, callback=self.parse_id, cookies=cookie)


    def parse_id(self, response):
        body = response.body.decode()
        pat = '"nid":"(.*?)"'
        allid = re.compile(pattern=pat).findall(body)
        for id in allid:
            url = 'https://item.taobao.com/item.htm?id='+str(id)
            item = TaobaoItem()
            item['id'] = id
            yield Request(url,callback=self.parse_good,meta={'item':item,},dont_filter=True)

    def parse_good(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        datas = soup.find('table', {'class': 'tm-tableAttr'}).find_all('tr')
        dic = {}
        item = response.meta['item']
        for td in datas:
            if (td.find('th') != None) and (td.find('td') != None):
                tdkey = td.find('th').get_text()
                tdval = td.find('td').get_text()
                tdval = "".join(tdval.split())
                a ={tdkey:tdval}
                dic.update(a)
        item['spec'] = dic
        yield item


