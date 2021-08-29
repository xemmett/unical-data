import scrapy
from datetime import datetime
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser
from json import load, dump


class BookSpider(scrapy.Spider):

    name = 'book_of_modules'

    start_urls = ['https://bookofmodules.ul.ie/']
    dsk_query = '' # bulk search query on libgen.rs
    module_count = 0
    book_of_modules = []
    module_required_texts = {}
    module_codes = []

    def __init__(self):
        with open(r'C:\Users\Emmett\magi-spiders\data\ul_course_timetables.json', 'r') as timetables:
            json_obj = load(timetables)
            for timetable in json_obj:
                for classes in timetable['class']:
                    self.module_codes.append(classes['module'])
        
    def parse(self, response):
        current_module = 0
        for module_code in self.module_codes:
            if(module_code not in self.module_codes[:current_module]):
                yield FormRequest.from_response(response, formdata={'ctl00$MasterContentPlaceHolder$ModuleDropDown': module_code, 'ctl00$MasterContentPlaceHolder$SubmitQuery.x': '4', 'ctl00$MasterContentPlaceHolder$SubmitQuery.y': '11'}, meta={'module':module_code}, callback=self.module_details)
            else:
                print('DUPLICATE:', current_module)
                current_module+=1
    
    def module_details(self, response):
        # open_in_browser(response)
                        
        module_info = {
            'module_code': 'Null',
            'module_title': 'Null',
            'required_hours': {},
            'prerequisites': 'Null',
            'purpose': 'Null',
            'syllabus': 'Null',
            'learning_outcomes': 'Null',
            'affective': 'Null',
            'pyschomotor': 'Null',
            'books': []
        }

        module_info['module_code'] = response.meta['module']

        module_code_title_element = (response.xpath('/html/body/form/div/div[2]/div[5]/div[3]/text()').getall())[1].split(' ')
        module_info['module_title'] = ' '.join([x for x in module_code_title_element if module_info['module_code'] not in x or x == ' ' and x != ''])
        module_info['module_title'] = module_info['module_title'].replace('-\r\n', '').strip()
        list_of_hours = response.xpath('/html/body/form/div/div[2]/div[5]/div[5]/*/text()').getall()
        list_of_hours = [x.replace(' ', '').replace('\r\n', '') for x in list_of_hours if x.replace(' ', '').replace('\r\n', '').isnumeric]
        list_of_deliveries = response.xpath('/html/body/form/div/div[2]/div[5]/div[5]/*/*/text()').getall()
        delivery = 0
        required_hours = {}
        for hours in list_of_hours:
            if(hours.isnumeric()):
                required_hours[list_of_deliveries[delivery]] = hours
                delivery+=1

        try:
            module_info['required_hours'] = required_hours
        except AttributeError as e:
            module_info['required_hours'] = 'Null'

        try:
            module_info['prerequisites'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[7]/div/text()').get().strip()
        except AttributeError as e:
            module_info['prerequisites'] = 'Null'
            
        try:
            module_info['purpose'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[8]/div/text()').get().strip()
        except AttributeError as e:
            module_info['purpose'] = 'Null'

        try:
            module_info['syllabus'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[9]/div/text()').get().strip()
        except AttributeError as e:
            module_info['syllabus'] = 'Null'

        try:
            module_info['learning_outcomes'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[11]/div/text()').get().strip()
        except AttributeError as e:
            module_info['learning_outcomes'] = 'Null'

        try:
            module_info['affective'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[12]/div/text()').get().strip()
        except AttributeError as e:
            module_info['affective'] = 'Null'
            
        try:
            module_info['pyschomotor'] = response.xpath('/html/body/form/div/div[2]/div[5]/div[13]/div/text()').get().strip()
        except AttributeError as e:
            module_info['pyschomotor'] = 'Null'

        book_details = response.xpath('//*[@id="ctl00_MasterContentPlaceHolder_ModuleFull_ListViewUpdatePanel"]/*')
        for data in book_details:
            title = data.xpath('h1/text()').get()
            if(title != None):
                title = title.strip()
                if('prime texts' in title.lower()):
                    for book in data.xpath('div'):
                        found_book = {
                            'publisher': 'Null',
                            'title': 'Null',
                            'edition': 'Null',
                            'year': 'Null',
                            'author': 'Null',
                            'required': "Yes",
                        }
                        author_publisher = (book.xpath('text()').getall())
                        author = author_publisher[0]
                        publisher = author_publisher[1].replace(',', '')
                        year_published = ''.join([word for word in author.split(" ") if ('20' in word or '19' in word) and (word.replace('(', ''))[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']])
                        found_book['author'] = author.replace(year_published, '').replace(')', '').replace('(', '').strip()
                        found_book['publisher'] = publisher.strip()
                        found_book['title'] = (book.xpath('i/text()').get()).strip()
                        found_book['edition'] = ''.join([word for word in found_book['title'].split(" ") if ('th' in word or 'rd' in word) and word[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']])
                        found_book['year'] = year_published.replace(')', '').replace('(', '')
                        
                        module_info['books'].append(found_book)
                
                elif('other relevant texts' in title.lower()):
                    for book in data.xpath('div'):
                        found_book = {
                            'publisher': 'Null',
                            'title': 'Null',
                            'edition': 'Null',
                            'year': 'Null',
                            'author': 'Null',
                            'required': "No",
                        }
                        author_publisher = (book.xpath('text()').getall())
                        author = author_publisher[0]
                        publisher = author_publisher[1].replace(',', '')
                        year_published = ''.join([word for word in author.split(" ") if ('20' in word or '19' in word) and (word.replace('(', ''))[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']])
                        found_book['author'] = author.replace(year_published, '').replace(')', '').replace('(', '').strip().replace("\\n", "").replace("\\", "")
                        found_book['publisher'] = publisher.strip()
                        found_book['title'] = (book.xpath('i/text()').get()).strip().replace('(', '').replace(')', '').replace("\\n", "").replace("\\", "")
                        found_book['edition'] = ''.join([word for word in found_book['title'].split(" ") if ('th' in word or 'rd' in word) and word[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']])
                        found_book['year'] = year_published.replace(')', '').replace('(', '')
                        
                        module_info['books'].append(found_book)
                    
        self.book_of_modules.append(module_info)
        print(self.book_of_modules)

    def closed(self, response):

        with open(r'C:\Users\Emmett\magi-spiders\data\ul_module_details.json', 'w+', encoding="utf-8") as of:
            dump(self.book_of_modules, of)