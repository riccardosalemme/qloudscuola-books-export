#################################### SETTINGS ####################################

# url della piattaforma (ricordarsi la / finale)
domain = "icpertinibusto.myqloud.eu"
url = f"http://{domain}/"

# immettere un valore anche superiore al numero di pagine (il programma si interrompe in automatico)
max_page = 1000

# digitare il nome della scuola
library = "BIBLIOTECA PERTINI"

# nome del file di output
output_file_name = "libri"

# Browser User Agent
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15'

################################## END SETTINGS ##################################

import requests
import pandas as pd

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'it-IT,it;q=0.9',
    'Host': domain,
    'User-Agent': user_agent,
    'Referer': url,
}

def get_books(page: int, school: str):
    params = {
        'a7_item_location': school, # 'BIBLIOTECA PERTINI',
        'lst': '1',
        'page': page,
    }
    response = requests.get(f'{url}data/api/opac/search/', params=params, headers=headers)
    return response.json()['records']

def get_book_data(book_id: str):
    response = requests.get(f'{url}data/api/opac/bib/{book_id}', headers=headers)
    data = response.json()['responseData']['record']

    barcodes = []
    instituteLibraries = []
    available_copies = 0
    for x in data['items']:
        barcodes.append(x['barcode'])
        instituteLibraries.append(x['location']['name'])
        if(x['status']['id'] == "available"):
            available_copies += 1

    barcodes = "-".join(barcodes)
    instituteLibraries = "-".join(instituteLibraries)

    return {
        "title" : data['title'].replace("/", "").replace(":", "").strip(),
        "titleDesc" : data['titleDesc'],
        "author" : data['author'],
        "isbnid" : data['isbnid'],
        "id" : data['id'],
        "copies" : len(data['items']),
        "barcodes" : barcodes,
        "availableCopies" : available_copies,
        "instituteLibraries" : instituteLibraries,
        "localCallNumber" : data['items'][0]['localCallNumber'] if len(data['items']) != 0 else "",
        "media" : data['items'][0]['media']['name'] if len(data['items']) != 0 and data['items'][0]['media'] else "",
        "collection" : data['items'][0]['collection']['name'] if len(data['items']) != 0 and data['items'][0]['collection'] else "",
    }


BOOKS = []

for i in range(1, max_page):
    books_list = get_books(i, library)

    if(len(books_list) == 0): # verifico se ho raggiunto l'ultima pagina
        break

    for book in books_list:
        book_id = book['id']
        BOOKS.append(get_book_data(book_id))

        print("Page", i, "-", book['title'])


df = pd.DataFrame(BOOKS)

# CSV Export
df.to_csv(f"{output_file_name}.csv")

# XLSX Export
with pd.ExcelWriter(f"{output_file_name}.xlsx") as writer:  
    df.to_excel(writer, sheet_name='Books')

print()
print("Totale libri esportati:", len(BOOKS))