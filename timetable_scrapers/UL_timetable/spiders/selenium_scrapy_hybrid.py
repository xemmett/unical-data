import scrapy
import os
from json import dump



class Scraper(scrapy.Spider):

    name = 'hybrid'
    directory = r'C:\Users\Emmett\magi-spiders\courses_webpages'

    start_urls = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            start_urls.append('file:///'+directory+'/'+filename)

    UL = []
    def parse(self, response):
        timetable = {}
        course_name_code = response.xpath('//*[@id="select2-HeaderContent_CourseDropdown-container"]/text()').get()
        course_name_code_list = response.xpath('//*[@id="select2-HeaderContent_CourseDropdown-container"]/text()').get().split(" ")
        course_code_w_brackets = course_name_code_list[len(course_name_code_list)-1]
        timetable['course_name'] = course_name_code.replace(course_code_w_brackets, '').strip()
        timetable['course_code'] = course_code_w_brackets.replace('(', '').replace(')', '')
        timetable['course_year'] = response.xpath('//*[@id="select2-HeaderContent_CourseYearDropdown-container"]/text()').get()
        timetable['class'] = []
        # open_in_browser(response)
        table = response.css('#MainContent_CourseTimetableGridView') # ~~~~~~~~~ Point the bot the table grid 
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
                            'day': 0,
                            'professor': 'Null',
                            'module': 'Null',
                            'group': 'Null',
                            'delivery': 'Null',
                            'location': 'Null',
                            'active_weeks': [],
                            'start_time': '00:00',
                            'end_time': '00:00'
                        }
                        times_list = my_classes[i].split(' - ')
                        module_list = my_classes[i+1].split(' - ')
                        new_class['day'] = day
                        new_class['module'] = module_list[0]
                        new_class['delivery'] = module_list[1]

                        try:   
                            new_class['group'] = module_list[2]
                        except IndexError as ie:
                            pass

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
                        
                        timetable['class'].append(new_class)
                        day_counter+=1

                    elif(i not in skip):
                        day_counter+=1
                else:
                    day_counter -= 1
        
        self.UL.append(timetable)
        return timetable

    def closed(self, response):
        with open(r'ul_course_timetables.json', 'w+', encoding='utf-8') as db:
            dump(self.UL, db)
            