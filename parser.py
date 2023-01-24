from selenium import webdriver
import time
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_page(url, filename):
    options = webdriver.ChromeOptions()
    user_agent = UserAgent()
    options.add_argument(f'user-agent={user_agent.chrome}')
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path='C:\\Users\\shved\\PycharmProjects\\price_parser\\chromedriver.exe',
                              options=options)
    driver.get(url)
    html = driver.page_source
    driver.close()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)


def parse_url(url):
    if 'dns' in url:
        service, product, price = parse_dns(url)
    elif 'ozon' in url:
        service, product, price = parse_ozon(url)
    elif 'citilink' in url:
        service, product, price = parse_citilink(url)
    elif 'yandex' in url:
        service, product, price = parse_yandex(url)
    else:
        return 'invalid url'
    if price[-1] == '₽':
        price = price[:-1]
    return service, product, price


def parse_dns(url):
    # if not os.path.isfile('dns_page.html'):
    get_page(url, 'dns_page.html')
    with open('dns_page.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    product = soup.find('h1', class_='product-card-top__title').text
    price = soup.find('div', attrs={'class': {'product-buy__price', 'product-buy__price_active'}}).text
    return 'DNS', product, price


def parse_ozon(url):
    # if not os.path.isfile('ozon_page.html'):
    get_page(url, 'ozon_page.html')
    with open('ozon_page.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    try:
        product = soup.find('h1', class_='o6r').text
    except Exception as e:
        product = soup.find('h1', class_='so').text
    try:
        price = soup.find('div', attrs={'class': {'p1o', 'po3', 'op5'}}).find_all('span')[1].text
    except Exception as e:
        price = soup.find('span', attrs={'class': {'po6', 'p6o'}}).text
    return 'Ozon', product, price.replace('\u2009', '')[:-1]


def parse_citilink(url):
    # if not os.path.isfile('citilink_page.html'):
    get_page(url, 'citilink_page.html')
    with open('citilink_page.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    product = soup.find('h1', attrs={'class': {'Heading Heading_level_1', 'ProductPageTitleSection__text'}}).text
    price = soup.find('span', attrs={'class': {'ProductPagePriceSection__default-price_current-price',
                                               'js--ProductPagePriceSection__default-price_current-price',
                                               'ProductPagePriceSection__default-price-value'}}).text
    return 'Citilink', product.strip(), price.strip()


def parse_yandex(url):
    # if not os.path.isfile('yandex_page.html'):
    get_page(url, 'yandex_page.html')
    with open('yandex_page.html', 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    product = soup.find('h1', attrs={'class': {'_1BWd_ _2OAAC undefined', 'cia-cs'}}).text
    price = soup.find('div', attrs={'class': {'_3NaXx', '_3kWlK'}}).find_all('span')[1].text
    return 'Yandex', product, price
