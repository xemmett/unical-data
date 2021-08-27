import scrapy
from datetime import datetime
from scrapy.http import FormRequest, Request
from scrapy.utils.response import open_in_browser

class Scraper(scrapy.Spider):

    name = 'time'
    start_urls = ['https://timetable.ul.ie/Login.aspx?ReturnUrl=%2fStudentTimetable.aspx']
    timetable = {}

    def __init__(self, student_id='18238831', pwd='Monday123'): # Input your ID number and password here to see orginal implementation
        self.timetable['class'] = []
        self.timetable['misc'] = {
            'id': '',
            'email': '',
            'pwd': '',
            'year': 0,
            'date_time': datetime.now().strftime('%d-%m-%y %H:%M')
        }
        self.timetable['misc']['id'] = student_id
        self.timetable['misc']['email'] = student_id+'@studentmail.ul.ie'
        self.timetable['misc']['pwd'] = pwd


    def parse(self, response):
        token = response.css('#__EVENTVALIDATION::attr(value)').extract_first()
        return FormRequest.from_response(response, formdata={"__EVENTVALIDATION": token, "TextBox_UserName":self.timetable['misc']['id'], "TextBox_Password":self.timetable['misc']['pwd']}, callback=self.LoggedIn)

    def LoggedIn(self, response):
        self.timetable['misc']['pwd'] = ''
        student_timetable_link = response.xpath('//*[@id="MainContent_StudentTile"]/a/@href').get()
        return response.follow(student_timetable_link, callback=self.GetTimetable)

    def GetTimetable(self, response):
        table = response.css('#MainContent_StudentTimetableGridView')
        days = [0, 1, 2, 3, 4, 5]
        for l in table:
            my_classes = l.css('td ::text').extract()
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
                            (self.timetable['misc'])['year'] = (my_classes[i+4])[-1:]
                            skip = [i+1, i+2, i+3, i+4]
                        else:
                            new_class['location'] = my_classes[i+3]
                            new_class['active_weeks'] = (my_classes[i+4]).replace('Wks:', '').split(',')
                            (self.timetable['misc'])['year'] = (my_classes[i+5])[-1:]
                            skip = [i+1, i+2, i+3, i+4, i+5]
                        
                        print(new_class)
                        
                        self.timetable['class'].append(new_class)
                        day_counter+=1

                    elif(i not in skip):
                        day_counter+=1
                else:
                    day_counter -= 1
        print(self.timetable)
        yield self.timetable

    