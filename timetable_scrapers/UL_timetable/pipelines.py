# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from icalendar import Calendar, Event, Alarm
from calendar import monthcalendar
from datetime import datetime, timedelta
from json import load, dump
from pytz import timezone

class UlTimetablePipeline:

    def writeics(self, calendar, student_id):
        with open('{}.ics'.format(student_id), 'wb') as ics_out:
            ics_out.write(calendar.to_ical())
    
    def writejson(self, timetable):
        try:
            with open('data.json', 'a', encoding='utf-8') as db:
                dump(timetable, db)
                db.write(',')
        except FileNotFoundError as fnf:
            with open('data.json', 'w+', encoding='utf-8') as db:
                dump(timetable, db)

    def process_item(self, item, spider):

        year = datetime.now().today().year
        month = datetime.now().today().month

        if(month > 7):
            #this is 2020 Winter semester
            academic_calendar = {
                    "1": ["9-28", "9-29", "9-30", "10-1", "10-2", "10-3", "10-4"], 
                    "2": ["10-5", "10-6", "10-7", "10-8", "10-9", "10-10", "10-11"], 
                    "3": ["10-12", "10-13", "10-14", "10-15", "10-16", "10-17", "10-18"], 
                    "4": ["10-19", "10-20", "10-21", "10-22", "10-23", "10-24", "10-25"], 
                    "5": ["10-26", "10-27", "10-28", "10-29", "10-30", "10-31", "11-1"], 
                    "6": ["11-2", "11-3", "11-4", "11-5", "11-6", "11-7", "11-8"], 
                    "7": ["11-9", "11-10", "11-11", "11-12", "11-13", "11-14", "11-15"], 
                    "8": ["11-16", "11-17", "11-18", "11-19", "11-20", "11-21", "11-22"], 
                    "9": ["11-23", "11-24", "11-25", "11-26", "11-27", "11-28", "11-29"], 
                    "10": ["11-30", "12-1", "12-2", "12-3", "12-4", "12-5", "12-6"], 
                    "11": ["12-7", "12-8", "12-9", "12-10", "12-11", "12-12", "12-13"], 
                    "12": ["12-14", "12-15", "12-16", "12-17", "12-18", "12-19", "12-20"]
                }    
        else:
            # 2021 Spring Semester
            academic_calendar = {
                    "1": ["1-25", "1-26", "1-27", "1-28", "1-29", "1-30", "1-31"], 
                    "2": ["2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7"], 
                    "3": ["2-8", "2-9", "2-10", "2-11", "2-12", "2-13", "2-14"], 
                    "4": ["2-15", "2-16", "2-17", "2-18", "2-19", "2-20", "2-21"], 
                    "5": ["2-22", "2-23", "2-24", "2-25", "2-26", "2-27", "2-28"], 
                    "6": ["3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7"], 
                    "7": ["3-8", "3-9", "3-10", "3-11", "3-12", "3-13", "3-14"], 
                    "8": ["3-15", "3-16", "3-17", "3-18", "3-19", "3-20", "3-21"], 
                    "9": ["3-22", "3-23", "3-24", "3-25", "3-26", "3-27", "3-28"], 
                    "10": ["3-29", "3-30", "3-31", "4-1", "4-2", "4-3", "4-4"], 
                    "11": ["4-5", "4-6", "4-7", "4-8", "4-9", "4-10", "4-11"], 
                    "12": ["4-12", "4-13", "4-14", "4-15", "4-16", "4-17", "4-18"], 
                    "13": ["4-19", "4-20", "4-21", "4-22", "4-23", "4-24", "4-25"]
                }

        c = Calendar()
        c.add('prodid', '-//imlate.studio//student calendar//EN')
        c.add('version', '2.0')

        for class_event in item['class']:
            
            active_weeks = class_event['active_weeks']
            # time_lists = [hour, minute]
            start_time = class_event['start_time'].split(':') 
            end_time = class_event['end_time'].split(':')
            duration_of_class = [int(end_time[0])-int(start_time[0]), int(start_time[1])-int(end_time[1])]

            for j in range(0, len(active_weeks)):
                active_weeks_list = active_weeks[j].split('-')
                print(active_weeks_list)
                start_week = active_weeks_list[0]
                start_date = (academic_calendar[start_week])[class_event['day']].split('-')
            
                try:
                    end_week = active_weeks_list[1] 
                    end_date = (academic_calendar[end_week])[class_event['day']].split('-')
                    interval = '1'
                except IndexError as e:
                    end_week = start_week 
                    end_date = start_date
                    interval = '1'

                class_time = datetime(year, int(start_date[0]), int(start_date[1]), int(start_time[0]), int(start_time[1]), 00, tzinfo=timezone("Europe/Dublin"))
                class_repeat_finish = datetime(year, int(end_date[0]), int(end_date[1]), int(end_time[0]), int(end_time[1]), 00)
                event_title = class_event['module'] + ' - ' + class_event['delivery']
                duration_of_class = 'P00DT'+str(duration_of_class[0])+'H'+str(duration_of_class[1])+'M00S'
                
                e = Event()
                e.add('SUMMARY', event_title)
                e.add('DTSTART', class_time)
                e['DURATION'] = duration_of_class
                e['TZID'] = 'Europe/Dublin'
                e['CALSCALE'] = 'GREGORIAN'
                e['LOCATION'] = class_event['location']
                e.add('RRULE', {'freq': 'weekly', 'interval': interval, 'wkst': 'MO', 'until': class_repeat_finish})
                
                a = Alarm()
                class_time = datetime(year, int(start_date[0]), int(start_date[1]), int(start_time[0]), int(start_time[1]), 00, tzinfo=timezone("Europe/Dublin")) - timedelta(minutes=5) # 10 mins before event
                a.add('TRIGGER', class_time)
                a.add('ACTION', 'AUDIO')
                a.add('DESCRIPTION', class_event['module'] + ' - ' + class_event['delivery'])
                
                e.add_component(a)
                c.add_component(e)
        
        # filename = item['student_id']
        # self.writeics(c, filename)
        # self.writejson(item)
        return item

