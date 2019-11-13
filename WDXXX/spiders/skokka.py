# -*- coding: utf-8 -*-
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.response import open_in_browser
from scrapy.http import Request
from scrapy.selector import Selector
from urllib.parse import urljoin

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

    #Region to scrapy
    REGION_TO_SEARCH = ['manaus']

    #START PAGE LINK
    ADVERTISEMENT_LINK = []

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.getSubType)

    def getSubType(self, response):
        types = response.xpath('//*[@id="categorie-ricerca"]/option/@value').extract()     

        for genre in types:
            self.subtype.append(str(genre))

        yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        
    def parse(self, response):
        for region in self.REGION_TO_SEARCH:
            for t in self.subtype:
                for x in range(self.QTT_PAGE_INDEX):
                    baseUrl = "%s/%s/%s" % (str(self.start_urls[0]), str(t),str(region))
                    abs_URL = str(baseUrl) + str("/?p=") + str(x+1)

                    yield scrapy.Request(url=abs_URL, 
                    callback=self.getAllAdByPage, cookies={'adult_cookie':'1'}, dont_filter=True)
        

    def getAllAdByPage(self, response):
        hxs = Selector(response)

        adLink = hxs.xpath('//*[@id="colonna-unica"]/div/div/div[2]/h3/a/@href').extract()

        #Remove duplicated
        uniqueLink = [x for i, x in enumerate(adLink) if i == adLink.index(x)]

        for link in uniqueLink:
            if link:                
                personLink = urljoin(self.start_urls[0], link)
                self.ADVERTISEMENT_LINK.append(personLink)
                yield Request(url=personLink, callback=self.getInfoByPerson, cookies={'adult_cookie':'1'}, dont_filter=True)

    def getInfoByPerson(self, response):
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
