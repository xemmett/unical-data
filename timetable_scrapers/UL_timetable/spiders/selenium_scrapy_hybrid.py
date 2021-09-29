import scrapy
import os
from json import dump
from time import strptime, sleep


class Scraper(scrapy.Spider):

    name = 'hybrid'
    directory = r'C:\Users\Emmett\magi-spiders\timetable_scrapers\course_webpages_2021'

    start_urls = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            start_urls.append('file:///'+directory+'/'+filename)
        
    start_urls = list(set(start_urls))

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
        rows = response.xpath('/html/body/form/div[5]/div/div/table/tbody/*') # ~~~~~~~~~ Point the bot the table grid 

        for row in rows[1:]:
            cells = row.xpath('td') #~~~~~ Use the table selector object to shortent the css path / xpath
            #
        #
            day = 0
            for cell in cells:
                data = cell.xpath('text()').getall()
                # ['09:00 - 11:00', 'EE4216 - LAB - 2B', ' HAYES (ECE) MARTIN DR', 'Wks:4,8,13']
                for c in data:
                    if(c == ' '):
                        data.remove(c)
                    elif(c==r'\xa0'):
                        break
        #
                if(data == []):
                    continue
        #
                print("data: ", data)
                start_index = 0
                for d in data:
                    start_index += 1
                    if(TimeCheck(d)):
                        subdata = [d]
                        for elem in data[start_index:]:
                            print('elem: ', elem)
                            if(TimeCheck(elem)):
                                break
                            else:
                                subdata.append(elem)
                        
                        print("subdata: ", subdata)
                        new_class = ProcessClassData(subdata, day)
                        print('processed: ', new_class)
                        timetable['class'].append(new_class)
        
                day+=1
            
        self.UL.append(timetable)
        return timetable

    def closed(self, response):
        filename = r'C:\Users\Emmett\magi-spiders\data\ul_course_timetables.json'
        with open(filename, 'w+') as db:
            dump(self.UL, db)

def TimeCheck(input):
    try:
        times = input.split('-')
        start_time = times[0].strip()
        end_time = times[1].strip()
        strptime(start_time, '%H:%M')
        strptime(end_time, '%H:%M')
        return True
    except ValueError:
        return False
    except IndexError:
        return False

def ProcessClassData(class_data, day):
    new_class = {
        'day': day,
        'professor': 'Null',
        'module': 'Null',
        'group': 'Null',
        'delivery': 'Null',
        'location': 'Null',
        'active_weeks': [],
        'start_time': '00:00',
        'end_time': '00:00'
    }
    #
    times = class_data[0].split('-')
    start_time = times[0].strip()
    end_time = times[1].strip()
    #
    class_desc = class_data[1].split('-')
    module = class_desc[0].strip()
    delivery = class_desc[1].strip()
    #
    try:
        group = class_desc[2].strip()
        new_class['group'] = group
    except IndexError as e:
        pass
    #
    try:
        professor = 'Unknown'
        location = ''
        if(len(class_data) < 5):
            # data missing
            unknown_data = class_data[-2].strip()
            location = unknown_data
            professor = unknown_data
        else:
            location = class_data[-2].strip()
            professor = class_data[2].strip()
        new_class['professor'] = professor
        new_class['location'] = location
    except IndexError as e:
        pass
    #
    active_weeks = class_data[-1].replace('Wks:', '').strip()
    active_weeks = active_weeks.split(',')
    #
    new_class['day'] = day
    new_class['start_time'] = start_time
    new_class['end_time'] = end_time
    new_class['module'] = module
    new_class['delivery'] = delivery
    new_class['active_weeks'] = active_weeks
    #           
    return new_class