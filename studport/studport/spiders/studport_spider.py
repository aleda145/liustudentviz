import os
import scrapy
from scrapy.http import FormRequest
from scrapy.http import Request
from studport.items import StudportItem
import re
import time
class Studport_spider(scrapy.Spider):
    name = "studport"
    # with open('./zip_codes.txt') as f:
    #     content=f.readlines()
    # zip_codes = [x.strip() for x in content]
    mail_list=[]
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
            with open('./zip_codes.txt') as f:
                for url in f.readlines():
                    yield scrapy.Request(url,
                        callback=self.parse_search_page)
            # yield scrapy.Request('https://www3.student.liu.se/portal/search?searchtext=%22584 32%22&search=Search',
            #     callback=self.parse_search_page, priority=1)

            # new_url='https://www3.student.liu.se/portal/search?searchtext=%22'+'581 28'+'%22&search=Search'
            # print(new_url)
            # #print(new_url)
            # yield Request(url=new_url,
            #                callback=self.parse_search_page)


    def get_details(self,response):
        #student = StudPortItem()
        #print('entered detail')
        resultarea = response.xpath('//*[@id="resultarea"]')
        name = resultarea.xpath('//h2/text()').extract()
        program = resultarea.xpath('tr[td[i[contains(text(), "Programregistreringar")]]]/td[2]/text()').extract()
        courses = resultarea.xpath('tr[td[i[contains(text(), "Kursregistreringar")]]]/td[2]/text()').extract()
        address = resultarea.xpath('tr[td[i[contains(text(), "Adress")]]]/td[2]/text()').extract()

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
        }



    def parse_search_page (self,response):
        #print('new page')
        resulttable = response.xpath('//*[@id="resulttable"]')
        #print(resulttable.extract())
        student_list=[]
        detail_list = (resulttable.xpath('tr/td/a[contains(text(), "Visa detaljer")]/@href').extract())
        for detail in detail_list:
            print(detail)
            mail = re.search('\mail=(.*)&displayedresults',detail)
            print(mail.group(1))
            yield {
            'mail' : mail.group(1)
            }
        #    print('entering detail')
            # yield response.follow(detail, self.get_details)

        next_page = response.xpath('//*[@id="resultarea"]/p/a[contains(text(), "sta 10")]/@href').extract_first()
        #print(next_page)

        if next_page:
            yield scrapy.Request('https://www3.student.liu.se/portal/search'+next_page,
            callback=self.parse_search_page)
        else:
            print('no new page')
            #print(self.mail_list)

        # for index,table_row in enumerate(resulttable.xpath('tr/td')):
        #
        #     #the td valign = kinda breaks the for loop but it's pretty hard to remove something using selectors. just making a different case of the first record.
        #     # if index==0:
        #     #     print(table_row.xpath('.//b/text()').extract()) #name remmeber to follow show deatils link here!
        #     if index % 11 == 3 :
        #         #print(table_row.xpath('.//i/text()').extract()) # program registration
        #         print(table_row.extract())
        #         #data_dict['program'] = table_row.extract()
        #         #this is obviously an ugly way to solve the string cleaning, but it works!
        #         program_raw = table_row.extract()
        #         program_raw1 = program_raw.replace('<td>', '')
        #         program_raw2 = program_raw1.replace('</td>', '')
        #         program_raw3 = program_raw2.replace('<i>', '')
        #         program = program_raw3.replace('</i>', '')
        #         print(program)
        #     if index % 11 == 5 :
        #         #print(table_row.xpath('.//td/text()').extract()) # address registration
        #         print(table_row.extract())
        #         #data_dict['address'] = table_row.extract()
        #         #print(data_dict)
        #         address_raw = table_row.extract()
        #         address_raw1 = re.sub(r'<td>.+?<br>','',address_raw)
        #
        #         # address_raw1 = address_raw.replace('<td>', '')
        #         address_raw2 = address_raw1.replace('</td>', '')
        #         address = address_raw2.replace('br', ' ')
        #         # address = address_raw3.replace('<>', '')
        #         print(address)
        #
        #         student = StudportItem()
        #         student['address'] = address
        #         student['program'] = program
        #     # print(table_row.extract())
        #     # print(index)
        #         yield student
        #print(resulttable.xpath('tr'))
            #print(index)
