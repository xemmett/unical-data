from selenium import webdriver
from time import sleep
from json import load
from re import sub

options = webdriver.ChromeOptions()
options.add_argument(r'user-data-dir=C:\Users\Emmett\AppData\Local\Google\Chrome\selenium profile')
driver = webdriver.Chrome(options=options)

with open(r'C:\Users\Emmett\magi-spiders\data\libgen_books.json') as libgen_file:
    libgen_books = load(libgen_file)

with open(r'C:\Users\Emmett\magi-spiders\data\ul_module_details.json') as ul_modules_file:
    ul_modules = load(ul_modules_file)

ul_module_books_per_module = [module['books'] for module in ul_modules]
ul_module_books = []

for books in ul_module_books_per_module:
    ul_module_books+=books

libgen_book_titles = [(sub(r'\([^)]*\)', '', book['title']).replace("\\n", "").replace("\\", "")).strip() for book in libgen_books]

ul_module_book_titles = [(sub(r'\([^)]*\)', '', book['title']).replace("\\n", "").replace("\\", "")).strip() for book in ul_module_books] # libgen title formatting

missing_downloadable_books = [book for book in ul_module_books if(book['title'] not in libgen_book_titles)]

amazon_books = []

for book in missing_downloadable_books:
    book_title = book['title']
    driver.get("https://affiliate-program.amazon.co.uk/home/productlinks/search")

    search_box = driver.find_element_by_xpath('//*[@id="search-product-field"]')
    search_box.send_keys(book_title)

    go_search = driver.find_element_by_xpath('//*[@id="a-autoid-2"]/span/input').click()

    sleep(5)
    results = driver.find_elements_by_xpath('/html/body/div[1]/div[4]/div/div[4]/div/div/div[2]/div/div/div[2]/table/tbody/*')

    distributor_relxpath = 'td[2]/ul/li[2]/span'
    book_title_relxpath = 'td[2]/ul/li[1]/span/a'

    resulting_books = []
    for result in results:
        try:
            distributor = result.find_element_by_xpath(distributor_relxpath)
            resulting_books.append(result)
        except:
            pass

    results_titles = [result.find_element_by_xpath(book_title_relxpath).text for result in resulting_books]

    print(results_titles)

    index=0
    match_found = False
    for result_title in results_titles:
        result_title = sub(r'\([^)]*\)', '', result_title).strip()
        if(result_title in book_title or book_title in result_title):
            match_found = True
        same_word_count = 0
        for word in book_title:
            if(word in result_title):
                same_word_count+=1
            if(same_word_count/len(book_title) >= 0.95):
                match_found = True
        if(match_found):
            break
        index+=1

    if(match_found):
        get_link = results[index].find_element_by_xpath('td[5]/div')
        get_link.click()

        text_only = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div[2]/div/div/div[2]/div/div[1]/ul/span[2]/li/a')
        text_only.click()

        display_link = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/div/span/fieldset/div[2]/label')
        display_link.click()

        link = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/span/textarea[2]').get_attribute('value')

        book['download_link'] = link
        book['amazon_affiliate'] = "yes"
        
        amazon_books.append(book)

    break

print(amazon_books)

driver.quit()