import scrapy

class resultSpider(scrapy.item):
    #Name of person
    name = scrapy.field()

    #Number to call, sometimes is same to whatsapp/telegram
    phone = scrapy.field()

    #Whatsapp/telegram number
    mobileChat = scrapy.field()

    #Age of person, please use just number
    age = scrapy.field()

    #city or region(the most of querys on site use it)
    region = scrapy.field()

    #Avatar or something like that
    img = scrapy.field()

    #Final URL That contains all data
    url = scrapy.field()

    #Google Style to create a contact on Android.
    vcf = scrapy.field()

    #The root of website.
    fromWebsite = scrapy.field()

    #type of genre
    genre = scrapy.field()

    #Description of AD
    adConetnt = scrapy.field()