import time
import requests
import schedule
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_book_data(book_url: str) -> dict:
   """
    Извлечение данных одной книги

    Берет адрес страницы (book_url)

    Возвращает словарь с информацией о книге:
        'title' - название
        'price' - цена
        'rating' - рейтинг
        'availability' - наличие
        'description' - описание
        'product_information' - полная информация
    """

   # НАЧАЛО ВАШЕГО РЕШЕНИЯ
   response = requests.get(book_url)
   response.raise_for_status()

   soup = BeautifulSoup(response.text, 'html.parser')

   title_tag = soup.find('h1')
   title = title_tag.text.strip() if title_tag else ''
   price_tag = soup.find('p', class_='price_color')
   price = price_tag.text.strip() if price_tag else ''

   rating_tag = soup.find('p', class_='star-rating')
   rating = 0
   if rating_tag:
      rating_class = rating_tag['class'][1]
      rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
      rating = rating_map.get(rating_class, 0)

   availability_tag = soup.find('p', class_='availability')
   availability = availability_tag.text.strip() if availability_tag else ''

   description = ''
   description_header = soup.find('div', id='product_description')
   if description_header:
      description_tag = description_header.find_next_sibling('p')
      if description_tag:
         description = description_tag.text.strip()

   product_info = {}
   table = soup.find('table', class_='table table-striped')
   if table:
      rows = table.find_all('tr')
      for row in rows:
         th = row.find('th')
         td = row.find('td')
         if th and td:
            product_info[th.text.strip()] = td.text.strip()

   book_data = {
      'title': title,
      'price': price,
      'rating': rating,
      'availability': availability,
      'description': description,
      'product_information': product_info
   }

   return book_data

   # КОНЕЦ ВАШЕГО РЕШЕНИЯ


def scrape_books(is_save: bool = False, max_workers: int = 10):
    """
    Парсинг всех страниц каталога
    
    Берет флаг сохранения информации (is_save) и 
    количество потоков для параллельных запросов (max_workers), нужно для ускорения
    
    Возвращает список словарей
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    catalogue_base = 'http://books.toscrape.com/catalogue/'
    page_template = catalogue_base + 'page-{}.html'
    total_pages = 50
    session = requests.Session()

    def fetch_page_links(page: int) -> list[str]:
        response = session.get(page_template.format(page))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return [catalogue_base + a['href']
                for a in soup.select('article.product_pod h3 a')]

    book_urls = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for links in pool.map(fetch_page_links, range(1, total_pages + 1)):
            book_urls.extend(links)

    def fetch_book(url: str) -> dict:
        return get_book_data(url)

    all_books = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(fetch_book, url) for url in book_urls]
        for future in as_completed(futures):
            all_books.append(future.result())

    if is_save:
        with open('artifacts/books_data.txt', 'w', encoding='utf-8') as f:
            for book in all_books:
                f.write(str(book) + '\n')

    return all_books

    # КОНЕЦ ВАШЕГО РЕШЕНИЯ


res = scrape_books(is_save=True) # Допишите ваши аргументы
print(type(res), len(res)) # и проверки