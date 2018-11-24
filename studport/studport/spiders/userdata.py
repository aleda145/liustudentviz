import os
import scrapy
from scrapy.http import FormRequest
from scrapy.http import Request
from studport.items import StudportItem
import re
import time
class userdata(scrapy.Spider):
    name = "userdata"
    # with open('./zip_codes.txt') as f:
    #     content=f.readlines()
    # zip_codes = [x.strip() for x in content]
    mail_list=[]
    custom_settings = {
    # specifies exported fields and order
    'FEED_EXPORT_FIELDS': ["name", "email", "program", "address", "courses"],
  }

    def start_requests(self):
        urls=[
        'https://www3.student.liu.se/portal/eng'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        return [FormRequest(url="https://www3.student.liu.se/portal/login",
                    formdata={'user': os.environ['LIU_USER_NAME'], 'pass2': os.environ['LIU_PASSWORD']},
                    callback=self.after_login)]


    def after_login(self,response):
        #check if u did it
        if "Wrong username" in response.body:
            self.logger.error('login failed')
            return

        else:
            print('logged in')
            with open('./mail_sorted.csv') as f:
                urls=[]
                for name in f.readlines():
                    urls.append('https://www3.student.liu.se/portal/search?searchtext='+name.rstrip()+'&search=S%F6k')
                print('loaded all urls')
                print(urls[0])
                for url in urls:
                    yield scrapy.Request(url,
                            callback=self.parse_search_page)
            # with open('./zip_codes.txt') as f:
            #     for url in f.readlines():
            #         yield scrapy.Request(url,
            #             callback=self.parse_search_page)
    def get_details(self,response):
        #student = StudPortItem()
        #print('entered detail')
        resultarea = response.xpath('//*[@id="resultarea"]')
        name = resultarea.xpath('//h2/text()').extract()
        program = resultarea.xpath('tr[td[i[contains(text(), "Programregistreringar")]]]/td[2]/text()').extract()
        courses = resultarea.xpath('tr[td[i[contains(text(), "Kursregistreringar")]]]/td[2]/text()').extract()
        address = resultarea.xpath('tr[td[i[contains(text(), "Adress")]]]/td[2]/text()').extract()
        email = resultarea.xpath('tr[td[i[contains(text(), "E-post")]]]/td[2]/a/@href').extract()

        # if not program:
        # #    print('no detail')
        #     program = 'Ingen Uppgift'
        # else:
        #     program=program[0]


        yield {
        'name' : name,
        'program' :program,
        'courses' : courses,
        'address' : address,
        'email' : email
        }

    def parse_search_page (self,response):
        #print('new page')
        resulttable = response.xpath('//*[@id="resulttable"]')
        #print(resulttable.extract())
        detail =resulttable.xpath('tr/td/a[contains(text(), "Visa detaljer")]/@href').extract()
        yield response.follow(detail[0], self.get_details)
