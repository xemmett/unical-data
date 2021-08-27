def lib_get(module_codes=[], booksdb =[]):
    
    found_books = []
    for book in booksdb:
        if(book['module_code'] in module_codes):
            book_client_info = {
                'author': book['author'],
                'title': book['title'],
                'download_link': book['download_link']
            }

            found_books.append(book_client_info)
    
    if(found_books == []):
        return ['Null']
    else:
        return found_books