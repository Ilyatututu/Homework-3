from unittest.mock import MagicMock, patch
from scraper import get_book_data, scrape_books

BOOK_URL = ('http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')

# данные о книге возвращаются в виде словаря с нужными ключами
def test_1():
    data = get_book_data(BOOK_URL)
    assert isinstance(data, dict)
    required_keys = {
        'title',
        'price',
        'rating',
        'availability',
        'description',
        'product_information'
    }
    assert required_keys.issubset(data.keys())

CATALOGUE_PAGE_HTML = '''
<html><body>
    <article class="product_pod">
        <h3><a href="book1_1/index.html">Book 1</a></h3>
    </article>
    <article class="product_pod">
        <h3><a href="book2_2/index.html">Book 2</a></h3>
    </article>
</body></html>
'''

# список ссылок или количество собранных книг соответствует ожиданиям
def test_2():
    mock_response = MagicMock()
    mock_response.text = CATALOGUE_PAGE_HTML
    mock_response.raise_for_status = MagicMock()

    with (
        patch('scraper.requests.Session.get', return_value=mock_response) as mock_get,
        patch('scraper.get_book_data', return_value={'title': 'Mock'}) as mock_book,
    ):
        result = scrape_books(is_save=False)

    assert isinstance(result, list)
    assert len(result) == 100
    assert mock_get.call_count == 50
    assert mock_book.call_count == 100

# значения отдельных полей (например, `title`) корректны
def test_3():
    data = get_book_data(BOOK_URL)
    assert isinstance(data['title'], str)
    assert 'Light in the Attic' in data['title']

