from calendar import monthcalendar, IllegalMonthError
from datetime import datetime
from json import dump

def calendar_dump(data, outfile_name):
    with open(outfile_name, 'w+') as outfile:
        dump(data, outfile)

def create_calendar(year, start_date, start_month, end_month):

    calendar = {}
    start_parsing = False
    start_date_string = '{}-{}'.format(start_month, start_date)
    academic_week = 1
    month_corrected = False
    for i in range(start_month, end_month):
        
        try:
            month = monthcalendar(year, i)
        except IllegalMonthError as e:
            break
        
        for j in range(1, len(month)):

            date_incrementer = 0
            week = []
            for date in month[j]:
                if date == 0:
                    if(i != 12 and month_corrected == False):
                        i+=1
                        month_corrected = True
                    date_incrementer+=1
                    date = date_incrementer

                date = '{}-{}'.format(str(i), str(date))
                week.append(date)
                
            if(start_date_string in week):
                start_parsing = True
            
            if(start_parsing):
                calendar[academic_week] = week
                academic_week+=1
                month_corrected = False
        

    return calendar_dump(calendar, 'academic_calendar.json')

def main():

    year = 2021
    month = 1


    if(month >= 6):
        start_month = 9
        end_month = 13
        start_date = 28
    else:
        start_month = 1
        end_month = 7
        start_date = 25

    return create_calendar(year, start_date, start_month, end_month)

main()