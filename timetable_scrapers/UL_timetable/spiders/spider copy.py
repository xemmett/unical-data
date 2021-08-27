import scrapy
from datetime import datetime
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser

class Scraper(scrapy.Spider):

    name = 'timetabler'
    start_urls = ['https://timetable.ul.ie/UA']
    timetable = {}
    modules = []
    module_counter = 0

    def __init__(self, module_codes=['EE4216'], student_id = '18238831'):
        self.modules = module_codes
        self.timetable['class'] = []
        self.timetable['student_id'] = student_id # student_profile['student_id']
        self.module_counter = 0

    def parse(self, response):
        # open_in_browser(response) 
        module_timetable_page_link = response.xpath("/html/body/form/div[5]/div/div/div[3]/a/@href").get() # /html/body/form/div[5]/div/div/div[4]/a
        return response.follow(module_timetable_page_link, callback=self.module_page)

    def module_page(self, response):
        # open_in_browser(response) 
        token = response.css('#__EVENTVALIDATION::attr(value)').extract_first()
        for module in self.modules:
            return FormRequest.from_response(response, formdata={"__EVENTTARGET": 'ctl00$HeaderContent$CourseDropdown', "ctl00$HeaderContent$CourseDropdown": 'LM037-Bachelor+of+Science+in+Economics+and+Mathematical+Sciences'}, headers={'Origin': 'https://timetable.ul.ie', 'Connection': 'keep-alive', 'Host': 'timetable.ul.ie', 'Referer': 'https://timetable.ul.ie/UA/CourseTimetable.aspx'}, callback=self.year_define)

    def year_define(self, response):
        open_in_browser(response) 
        token = response.css('#__EVENTVALIDATION::attr(value)').extract_first()
        yield FormRequest.from_response(response, formdata={"__EVENTVALIDATION": token, "__EVENTTARGET": 'ctl00$HeaderContent$CourseDropdown', "ctl00$HeaderContent$CourseDropdown": 'LM037-Bachelor+of+Science+in+Economics+and+Mathematical+Sciences', "ctl00$HeaderContent$CourseYearDropdown": '4'}, headers={'Origin': 'https://timetable.ul.ie', 'Referer': 'https://timetable.ul.ie/UA/CourseTimetable.aspx'}, callback=self.GetTimetable)

    def GetTimetable(self, response):
        # open_in_browser(response)
        table = response.css('#MainContent_ModuleTimetableGridView') # ~~~~~~~~~ Point the bot the table grid 
        days = [0, 1, 2, 3, 4, 5]
        for l in table:
            my_classes = l.css('td ::text').extract() #~~~~~ Use the table selector object to shortent the css path / xpath
            day_counter = 0
            skip = []
            for i in range(len(my_classes)-1):

                if(my_classes[i] != ' '):
                    
                    try:
                        day = days[day_counter]
                    except IndexError as e:
                        day_counter = 0
                        day = days[day_counter]

                    if(my_classes[i] != '\xa0' and i not in skip):

                        skip = []
                        new_class = {
                            'day': '',
                            'professor': '',
                            'module': '',
                            'delivery': '',
                            'location': '',
                            'active_weeks': [],
                            'start_time': '',
                            'end_time': ''
                        }

                        times_list = my_classes[i].split(' - ')
                        module_list = my_classes[i+1].split(' - ')
                        new_class['day'] = day
                        new_class['module'] = module_list[0]
                        new_class['delivery'] = module_list[1]
                        new_class['start_time'] = times_list[0]
                        new_class['end_time'] = times_list[1]
                        new_class['professor'] = (my_classes[i+2])[1:]

                        if('campus' not in my_classes[i+5]):
                            new_class['location'] = 'Online'
                            new_class['active_weeks'] = (my_classes[i+3]).replace('Wks:', '').split(',')
                            skip = [i+1, i+2, i+3, i+4]
                        else:
                            new_class['location'] = my_classes[i+3]
                            new_class['active_weeks'] = (my_classes[i+4]).replace('Wks:', '').split(',')
                            skip = [i+1, i+2, i+3, i+4, i+5]
                        
                        print(new_class)
                        
                        self.timetable['class'].append(new_class)
                        day_counter+=1

                    elif(i not in skip):
                        day_counter+=1
                else:
                    day_counter -= 1
        self.module_counter+=1
        if(self.module_counter == len(self.modules)):
            return self.timetable