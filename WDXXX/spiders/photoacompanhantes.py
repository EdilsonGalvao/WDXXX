import scrapy
from scrapy.http import Request
import os
from urllib.parse import urljoin
from scrapy.crawler import CrawlerProcess
import re

class PhotoacompanhantesSpider(scrapy.Spider):
    name = 'photoacompanhantes'
    start_urls = ['https://photoacompanhantes.com/acompanhantes/amazonas/manaus']
    init_url = ['https://photoacompanhantes.com']

    #Contains all subtypes of persons (like Girls, mens, shamale, etc...)
    subtype = ['acompanhantes']
    #Delay between pages 
    download_delay = 0.5
    #Quantity of pages
    QTT_PAGE_INDEX = 30

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.getSubType)

    def getSubType(self, response):
        #The combobox isn't equal to URL, anyway, 
        #I added it to keep solution generic the maximum as possible
        types = response.xpath('//*[@id="sectores"]/span/a/text()').getall()

        for tp in types:
            self.subtype.append(str(tp.lower()))

        yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        
    def parse(self, response):
        print("-------------------------")
        print("Started XXX Crawler: ")

        for t in self.subtype:
            mid = '%s/amazonas/manaus' % str(t)

            for x in range(self.QTT_PAGE_INDEX):
                abs_URL = "%s/%s/%s" % (str(self.init_url[0]), str(mid), str(x+1))

                yield Request(response.urljoin(abs_URL), callback=self.getAllAdByPage, dont_filter=True)        

    def getAllAdByPage(self, response):
        print("Looking Ads on: "+ response.url)
    
        err = response.xpath('//*[@class="no_encontrado"]/img/@alt').extract()

        #There are two ways to recovery link of persons
        linksHref = response.xpath('//*[@class="link_anuncio"]/@href').extract()
        linksData = response.xpath('//*[@class="anuncio top_off"]/@data-src').extract()

            #Join both list
        links = linksHref + linksData

            #Remove duplicated
        uniqueLink = [x for i, x in enumerate(links) if i == links.index(x)]

        for link in uniqueLink:                
            personLink = urljoin(self.init_url[0], link)
            yield Request(personLink, callback=self.getInfoByPerson, dont_filter=True)
        
        print("Looking Ads on: "+ response.url)

    def getInfoByPerson(self, response):
        #Name of Person
        name = self.validateParameter(response.xpath('//*[@id="anuncio_nombre"]/text()').get())

        #Whatsapp Number
        wpp = ''.join(re.findall('\d+', self.validateParameter(response.xpath('//*[@id="anuncio_telefono"]/span/@data-telefono').get())))

        #Other Number (Tradicional phone number)
        moboNumber = ''.join(re.findall('\d+', str(self.validateParameter(response.xpath('//*[@class="boton_texto"]/text()').get()))))
        if not wpp:
            wpp = moboNumber

        #Profile Image on Website
        img = self.validateParameter(response.xpath('//*[@id="anuncio_imagen_portada"]/@src').get())

        #City or State
        region = self.validateParameter(response.xpath('//*[@id="anuncio_poblacion"]/text()').get())

        #Age formatted as a number
        age = ''.join(re.findall('\d+', str(self.validateParameter(response.xpath('//*[@id="anuncio_edad"]/text()').get()))))

        #Google CSV Contact format 
        genre = "travestis" if "travestis" in response.url else "acompanhantes"
        details = ''
        vcf = self.Parser2VCF(self, name, wpp, details, response.url, genre)

        yield {
            'name': name,
            'phone': moboNumber,
            'whatsApp': wpp,
            'age': age,
            'region': region,
            'img': img,
            'url': response.url,
            'vcf': vcf,
            'from' : self.name,
            'category' : genre
        }

    def Parser2VCF(self, name, number, details, fromwebsite, genre):

        fullname = F'zzz - {name}'
        mail = 'wd@xxx.com'
        company = self.name

        #CSV Header
        #Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Language,Photo,Group Membership,E-mail 1 - Type,E-mail 1 - Value,Phone 1 - Type,Phone 1 - Value,Address 1 - Type,Address 1 - Formatted,Address 1 - Street,Address 1 - City,Address 1 - PO Box,Address 1 - Region,Address 1 - Postal Code,Address 1 - Country,Address 1 - Extended Address,Organization 1 - Type,Organization 1 - Name,Organization 1 - Yomi 

        return F'{fullname},{fullname},,,,,,,,,,,,,,,,,,,,,,,,{details},,,* myContacts ::: * starred,* Home,{mail},Work,{number},,{company},,{genre},,,,,,{fromwebsite}'

    def validateParameter(self, data):        
        try:
            if not data:
                return ''

            return data
        except:             
            return ''

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'items.json'
})

process.crawl(PhotoacompanhantesSpider)
process.start()
