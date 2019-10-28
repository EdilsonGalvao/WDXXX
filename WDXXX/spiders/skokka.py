# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.response import open_in_browser
from scrapy.http import Request

class SkokkaSpider(scrapy.Spider):
    name = 'skokka'
    allowed_domains = ['br.skokka.com/']
    start_urls = ['http://br.skokka.com']

    #Contains all subtypes of persons (like Girls, mens, shamale, etc...)
    subtype = []
    #Delay between pages 
    download_delay = 0.5
    #Quantity of pages
    QTT_PAGE_INDEX = 1

    REGION_TO_SEARCH = 'manaus'

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.getSubType)

    def getSubType(self, response):
        types = response.xpath('//*[@id="categorie-ricerca"]/option/@value').extract()     

        for genre in types:
            self.subtype.append(str(genre))

        yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse(self, response):
        for t in self.subtype:
            for x in range(self.QTT_PAGE_INDEX):
                baseUrl = "%s/%s/%s" % (str(self.start_urls[0]), str(t),str(self.REGION_TO_SEARCH))
                abs_URL = str(baseUrl) + str("/?p=") + str(x+1)

                yield scrapy.Request(url=abs_URL, cookies={'adult_cookie':'1'}, callback=self.getAllAdByPage, dont_filter=True)

    def getAllAdByPage(self, response):
        open_in_browser(response)
        links = response.xpath('//*[@class="annuncio row addctt"]/div[3]/h3/a/@href').extract() 
        pass

#this type of site blocked the Scrapy default agent, it was necessary change it. 
#I used this site to simulate my real user agent. 
#(https://www.whoishostingthis.com/tools/user-agent/) 

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'SkokkaSpider.json',
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
})

process.crawl(SkokkaSpider)
process.start()
