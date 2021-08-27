from ics_writer import create_ics, write_ics
from library_get import lib_get
from json import load
from sys import argv

def main():
    if __name__ == "__main__":
        course_code = argv[1]
        course_year = argv[2]

        electives_flag = 0
        ics_file_path = 'ERROR:NOCOURSE'
        library = []

        try:
            course_modules = argv[3].split(",")
            electives_flag = 1
        except IndexError as no_modules_specified:
            electives_flag = 0

        for course in coursedb:
            
            if(course['course_code'] == course_code):
                if(course['course_year'] == course_year):
                    if(electives_flag == 0):
                        classes = course['class']
                    else:
                        classes = [_class for _class in course['class'] if _class['module'] in course_modules]

                    try:
                        list_of_modules = [_class['module'] for _class in classes]
                        if( len(list_of_modules) != 0 ):

                            calendar = create_ics(classes)
                            ics_file_path = write_ics(calendar, 'timetable')
                            library = lib_get(list_of_modules, booksdb)

                        else:
                            # Chosen Modules don't exist.
                            ics_file_path = "ERROR:NOMODULES"
                        
                    
                    except NameError as e:
                        ics_file_path = 'ERROR:NOCOURSE'
        
        results = [{
            'ics_file':ics_file_path,
            'books':library
            }]

        print(ics_file_path)
        print(library)
        return results

booksdb = load(open('/mnt/c/users/xemme/magi/webapp/backend/databases/libgen_books.json', 'r'))
coursedb = load(open('/mnt/c/users/xemme/magi/webapp/backend/databases/ul_course_timetables_filtered.json', 'r'))
main()


