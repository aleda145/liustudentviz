import os
import scrapy
from scrapy.http import FormRequest
from scrapy.http import Request
from studport.items import StudportItem
import re

class Studport_spider(scrapy.Spider):
    name = "studport"
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
            return Request(url="https://www3.student.liu.se/portal/search?searchtext=%22584+32%22&search=Search",
                   callback=self.parse_search_page)

    def parse_search_page (self,response):
        print('new page')
        resulttable = response.xpath('//*[@id="resulttable"]')
        student_list=[]
        for index,table_row in enumerate(resulttable.xpath('tr/td')):

            #the td valign = kinda breaks the for loop but it's pretty hard to remove something using selectors. just making a different case of the first record.
            # if index==0:
            #     print(table_row.xpath('.//b/text()').extract()) #name remmeber to follow show deatils link here!
            if index % 11 == 3 :
                #print(table_row.xpath('.//i/text()').extract()) # program registration
                print(table_row.extract())
                #data_dict['program'] = table_row.extract()
                #this is obviously an ugly way to solve the string cleaning, but it works!
                program_raw = table_row.extract()
                program_raw1 = program_raw.replace('<td>', '')
                program_raw2 = program_raw1.replace('</td>', '')
                program_raw3 = program_raw2.replace('<i>', '')
                program = program_raw3.replace('</i>', '')
                print(program)
            if index % 11 == 5 :
                #print(table_row.xpath('.//td/text()').extract()) # address registration
                print(table_row.extract())
                #data_dict['address'] = table_row.extract()
                #print(data_dict)
                address_raw = table_row.extract()
                address_raw1 = re.sub(r'<td>.+?<br>','',address_raw)

                # address_raw1 = address_raw.replace('<td>', '')
                address_raw2 = address_raw1.replace('</td>', '')
                address = address_raw2.replace('br', ' ')
                # address = address_raw3.replace('<>', '')
                print(address)

                student = StudportItem()
                student['address'] = address
                student['program'] = program
            # print(table_row.extract())
            # print(index)
                yield student
        #print(resulttable.xpath('tr'))
            #print(index)
