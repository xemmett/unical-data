from pandas import read_json
from json import dump

def modules_per_course():
    timetables = read_json(open("ul_course_timetables.json", mode="r", encoding="utf8"))

    timetables = timetables[["course_code", "class", "course_year"]]
    timetables["unique_module_groups"] = ""

    courses = []

    for i,row in timetables.iterrows():
        classes = []
        for item in row['class']:
            new_class = {
                "professor": item['professor'].title(),
                "module": item['module'],
                "group": item['group'],
                # "delivery": item['delivery'],
            }

            if(new_class not in classes):
                classes.append(new_class)

        courses.append({
                "course_code": row['course_code'],
                "course_year": row['course_year'],
                "classes": classes
            })

    with open("module_course_details.json", "w+", encoding="utf8") as of:
        dump(courses, of, indent=6)
    
modules_per_course()