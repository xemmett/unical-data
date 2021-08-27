from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()
driver.get("https://timetable.ul.ie/UA/")

cookies_accept = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"]'
driver.find_element_by_xpath(cookies_accept).click()

course_timetable = '//*[@id="ctl01"]/div[5]/div/div/div[3]/a'
driver.find_element_by_xpath(course_timetable).click()
ul_courses = {}
num_of_courses = 0
num_of_years = 0
for i in range(2, 216):
    num_of_courses+=1
    course_chooser = '//*[@id="select2-HeaderContent_CourseDropdown-container"]'
    try:
        driver.find_element_by_xpath(course_chooser).click()
        course = '/html/body/span/span/span[2]/ul/li[{}]'.format(i)
        course_name = driver.find_element_by_xpath(course).text
        driver.find_element_by_xpath(course).click()
        
        for year in range(2, 8):
            num_of_years+=1
            sleep(5)
            driver.find_element_by_xpath('/html/body/form/div[4]/div/span[2]/span[1]/span/span[1]').click()

            try:
                course_year_sel = '/html/body/span/span/span[2]/ul/li[{}]'.format(year)
                course_year = driver.find_element_by_xpath(course_year_sel).text
                driver.find_element_by_xpath(course_year_sel).click()
                with open('./courses_webpages/{}.html'.format(course_name+'_'+course_year), 'w+') as of:
                    of.write(driver.page_source)
            except:
                break
    except:
        pass

driver.quit()