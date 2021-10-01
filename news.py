import investpy
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def get_news(ticker):
    search_result = investpy.search_quotes(text=ticker, products=['stocks'],
                                       countries=['united states'], n_results=1)
    url = 'https://www.investing.com'+search_result.tag+'-news'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req)
    soup1 = BeautifulSoup(webpage, 'html.parser')
    coverpage_news = soup1.find_all('a', class_= 'title')

    news = []
    for article in list(coverpage_news):
        news.append(article.get_text())
    return news[6:]
