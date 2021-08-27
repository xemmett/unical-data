# This will return a json of the full course, for selection by the user.

from ics_writer import create_ics, write_ics
from library_get import lib_get
from json import load
from sys import argv

def main():
    if __name__ == "__main__":
        course_code = argv[1]
        course_year = argv[2]

        electives_flag = 0
        timetable = 'ERROR:NOCOURSE'
        results = [{
            'timetable':[],
            'list_of_modules':[],
        }]

        for course in coursedb:
            
            if(course['course_code'] == course_code):
                if(course['course_year'] == course_year):
                    timetable = course['class']
                    list_of_modules = []
                    seen_modules = []

                    for _class in timetable:
                        if(_class['group'] == 'Null'):
                            _class['group'] = ''

                        module_details = {
                            'professor': _class['professor'],
                            'module': _class['module']
                            }

                        if(module_details not in seen_modules):
                            list_of_modules.append(module_details)
                            seen_modules.append(module_details)
                    
                    
                    if( len(list_of_modules) != 0 ):
                        results = {
                            'timetable':timetable,
                            'list_of_modules':list_of_modules,
                        }
        
        print(results['timetable'])
        print(results['list_of_modules'])
        return results

coursedb = load(open('/mnt/C/Users/Emmett/magi-master/backend/databases/ul_course_timetables_filtered.json', 'r'))
main()


