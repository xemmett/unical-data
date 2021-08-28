import scrapy
from datetime import datetime
from json import load, dump
from io import UnsupportedOperation
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser


class BookSpider(scrapy.Spider):

    name = 'libgen_spider'

    start_urls = ['http://libgen.rs/batchsearchindex.php']

    libgen_found_books = []
    
    def parse(self, response):
        with open(r'C:\Users\xemme\Documents\Python Scripts\timetable_scraper\webapp\backend\databases\ul_module_details.json', 'r', encoding="utf-8") as modules:
            module_details = load(modules)
            for module in module_details:
                dsk_query = ''

                for book in module['books']:
                    # ~~ temporary fix for edition, bookofmodules.py failed to see editions in brackets e.g "(8th edition)"
                    # code is from bookofmodules.py so is fixed for next semester
                    
                    book['title'] = book['title'].replace('(', '').replace(')', '').replace("\\n", "").replace("\\", "")
                    book['edition'] = ''.join([word for word in book['title'].split(" ") if ('th' in word or 'rd' in word) and word[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']])
                    #~~~~ end of bug fix

                    book['module_code'] = module['module_code']
                    book['search_string'] = book['title']

                    if(book['edition'] != ''):
                        search_string = book['title'].split(book['edition'])[0]
                        book['search_string'] = search_string

                    dsk_query += book['search_string']+'\r\n'
                
                print(dsk_query)
                yield FormRequest('http://libgen.rs/batchsearchindex.php', meta={'books': module['books']}, formdata={'dsk': dsk_query}, callback=self.results_per_book)

    def results_per_book(self, response):

        books = response.meta['books']
        
        query_link = (response.xpath('/html/body/table/tr/td/a/@href')).getall()
        query_text = (response.xpath('/html/body/table/tr/td/text()')).getall()
        required_text_index = 0
        link_incrementer = 0
        book_incrementer = 0
        
        for i in range(0, len(query_text)-1, 2):
            if(int(query_text[i+1]) > 0):
                link = query_link[link_incrementer]
                print(books[book_incrementer])
                yield response.follow(link, meta={'query_link': query_link[link_incrementer], 'book': books[book_incrementer]}, callback=self.get_book)
            
            book_incrementer+=1
            required_text_index+=1
            link_incrementer+=1

    def get_book(self, response):
        # open_in_browser(response)

        module_book = response.meta['book']
        module_book_author = module_book['author'].replace(',', '').replace('.', '').replace(';', '').replace('\'', '')
        module_book_title = module_book['title']
        print(module_book_title)
        i=0
        result_count=0
        lrg_sml_mb = []
        result_sizes = []
        result_mirrors = []
        result_authors = []
        result_years = []
        result_languages = []
        book_search_results = []

        # results_file_sizes = [int(x.xpath("text()").get().replace(' Mb', '')) for x in (response.xpath("/html/body/table[3]/*/*"))[11:] if 'Mb' in x.get()]
        # results_mirrors = [x.xpath('@href').get() for x in (response.xpath("/html/body/table[3]/*/*/*"))[11:] if '[1]' in x.get()]
        # print((response.xpath("/html/body/table[3]/*/*"))[11:])

        for result in (response.xpath("/html/body/table[3]/*/*"))[11:]:
            author_link = ''
            mirror = ''

            author_link = result.xpath('*/@href').get()
            mirror = result.xpath('*').get()

            try:
                if('author' in author_link):
                    try:
                        result_author = result.xpath('*/text()').get().replace(',', '').replace(';', '').replace('.', '').replace('\'', '')
                    except:
                        result_author = 'Null'
                    result_authors.append(result_author)

                elif('[1]' in mirror):
                    result_mirrors.append(result.xpath('*/@href').get())

            except TypeError as e:
                item = result.xpath('text()').get()
                if(item == None):
                    break

                elif(' Mb' in item):
                    size = int(item.replace(' Mb', ''))

                    result_sizes.append(size)
                    lrg_sml_mb.append(size)

                elif(' Kb' in item):
                    size = int(item.replace(' Kb', ''))

                    result_sizes.append(size/1000)
                    lrg_sml_mb.append(size/1000)

                elif(item.isnumeric() and ('20' in item or '19' in item) and len(item) == 4):
                    result_years.append(item)

                elif(item.isalpha()):
                    result_languages.append(item)
            
                # print(result_sizes)
                # print(result_authors)
                # print(result_mirrors)
        lrg_sml_mb.sort(reverse=True)
        unique_languages = list(set(result_languages))
        
        for mb in lrg_sml_mb:
            working_index = result_sizes.index(mb)
            
            # print(module_required_text_author, '\n', result_authors[working_index])
            author_verify = [x for x in module_book_author.split(" ") if x in result_authors[working_index] and len(x)>1]
            double_author_verify = [x for x in result_authors[working_index].split(" ") if x in module_book_author and len(x)>1]

            if(len(author_verify) > 0 or len(double_author_verify)>0):
                print('mb, lrg_sml_mb', mb, lrg_sml_mb)
                final_mirror = result_mirrors[working_index]
                print(author_verify)
                print(final_mirror)
                try:
                    module_book['found_year'] = result_years[working_index]
                except IndexError as e:
                    module_book['found_year'] = 0
                try:
                    module_book['found_language'] = result_languages[working_index]
                except IndexError as e:
                    module_book['found_language'] = 'Null'
                    
                module_book['found_author'] = result_authors[working_index]
                yield Request(final_mirror, meta={'module_book': module_book}, callback=self.get_download_link)
                break

    def get_download_link(self, response):
        # open_in_browser(response)
        module_book = response.meta['module_book']
        download_link = (response.css("#download > h2:nth-child(1) > a:nth-child(1)")).xpath("@href").get()
        module_book['download_link'] = str(download_link)

        self.libgen_found_books.append(module_book)

    def closed(self, response):

        with open(r'C:\Users\xemme\Documents\Python Scripts\timetable_scraper\webapp\backend\databases\libgen_books.json', 'w+', encoding='utf-8') as output:
            records = self.libgen_found_books
            dump(records, output)

