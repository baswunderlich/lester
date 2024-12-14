import requests
from bs4 import BeautifulSoup
import sys
import threading
import json
import os 
from newsplease import NewsArticle, NewsPlease
import datetime
import time
import random

sabc_active = sys.argv.count("sabc") > 0 or sys.argv.count("all") > 0
moscowtimes_active = sys.argv.count("moscowtimes") > 0 or sys.argv.count("all") > 0
rferl_active =sys.argv.count("rferl") > 0 or sys.argv.count("all") > 0
chinadaily_active =sys.argv.count("chinadaily") > 0 or sys.argv.count("all") > 0
spiegel_active = sys.argv.count("spiegel") > 0 or sys.argv.count("all") > 0
cnn_active = sys.argv.count("cnn") > 0 or sys.argv.count("all") > 0
folha_active = sys.argv.count("folha") > 0 or sys.argv.count("all") > 0
tass_active = sys.argv.count("tass") > 0 or sys.argv.count("all") > 0
kyiv_active = sys.argv.count("kyiv") > 0 or sys.argv.count("all") > 0

def get_kyiv_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 1
    enough_articles = False

    while not enough_articles:
        url = f"https://www.kyivpost.com/search?q=climate&page={page_index}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("div", {"class": "title"})
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                href = a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)} articles from Kyiv (Ukraine) fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_tass_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 0
    enough_articles = False

    while not enough_articles:
        url = f"https://tass.com/userApi/search"
        body = {
            "type":
                [
                    "default",
                    "article"
                ],
            "sections": [],
            "searchStr":"climate",
            "range": None,
            "sort":"date",
            "from":page_index*20,
            "size":(page_index+1)*20
        }
        raw_response = requests.post(url, json=body)
        response = json.loads(raw_response.text)

        for article in response[:3]:
            href = "https://tass.com" + article["link"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)} articles from Tass (Russia) fetched")
        if len(article_urls) > 0 and len(article_urls) % 51 == 0:  #51 damit durch 3 teilbar (drei Artikel von jeder Seite)
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_folha_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 0
    enough_articles = False
    last_id : int = None

    while not enough_articles:
        url = f"https://search.folha.uol.com.br/search?q={keyword}&site%5B%5D=internacional%2Fen&periodo=todos&sr={page_index*50+1}&results_count=382&search_time=0%2C022&url=https%3A%2F%2Fsearch.folha.uol.com.br%2Fsearch%3Fq%3Dclimate%26site%255B%255D%3Dinternacional%252Fen%26periodo%3Dtodos%26sr%3D51"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("div", {"class": "c-headline__content"})
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                href = a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)} articles from Folha (south america) fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_cnn_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 0
    enough_articles = False

    while not enough_articles:
        url = f"https://search.prod.di.api.cnn.io/content?q={keyword}&size=10&from={page_index * 10 + 1}&page={page_index+1}&sort=newest&types=article&request_id=pdx-search-27d868fa-19d7-45fc-b0c2-e444513d3d72"
        raw_response = requests.get(url)
        response = json.loads(raw_response.text)
        results = response["result"]

        for r in results:
            href = r["url"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)} articles from cnn fetched")
            if len(article_urls) > 0 and len(article_urls) % 50 == 0:
                if is_article_too_old(article_urls[-1]):
                    enough_articles = True
        page_index += 1
        time.sleep(random.choice(range(5)))
    return article_urls

def get_spiegel_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 1
    enough_articles = False

    while not enough_articles:
        url = f"https://www.spiegel.de/services/sitesearch/search?segments=spon_international&q={keyword}&after=-2208988800&before=1733078189&page_size=20&page={page_index}"
        response = json.loads(requests.get(url).text)
        results = response["results"]

        for r in results:
            href = r["url"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)} articles from spiegel fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                return article_urls
        page_index += 1
    return article_urls

def get_moscowtimes_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 1

    url = f"https://www.themoscowtimes.com/api/search?query={keyword}&section=news"
    response = json.loads(requests.get(url).text)
    for i in range(min(len(response), 300)):
        href = response[i]["url"]
        article_urls.append(href)
    return article_urls

def get_sabc_article_urls(keyword: str) -> []:
    article_urls = []
    page_index = 1
    enough_articles = False

    while not enough_articles:
        url = f"https://www.sabcnews.com/sabcnews/page/{page_index}/?s={keyword}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("article")
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                href = a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)} articles from SABC fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_rferl_article_urls(keyword: str):
    article_urls = []
    page_index = 1
    enough_articles = False
    
    while not enough_articles:
        url = f"https://www.rferl.org/s?k={keyword}&tab=news&pi={page_index}&r=any&pp=50"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("div", {"class": "media-block"})
        for _, article in enumerate(articles, start=5):
            a_s = article.find_all("a")
            for a in a_s:
                #At this site. The hrefs do not include the serveradresse.
                #Therefore it needs to be added
                href = "https://www.rferl.org" + a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)} articles from rferl fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_chinadaily_article_urls(keyword: str):
    article_urls = []
    #Chinadaily starts with the pageIndex 0
    page_index = 0
    enough_articles = False

    while not enough_articles:
        #Using chindailys advanced search
        # url = f"https://newssearch.chinadaily.com.cn/rest/en/search?publishedDateFrom=2018-01-01&publishedDateTo=2024-12-05&fullMust=climate&channel=&type=&curType=story&sort=dp&duplication=on&page=0&type[0]=story&channel[0]=2@cndy&source="
        url = f"https://newssearch.chinadaily.com.cn/rest/en/search?keywords={keyword}&sort=dp&page={page_index}&curType=story&type=&channel=&source="
        page = requests.get(url)
        page_decoded = json.loads(page.text)

        for article in page_decoded["content"][:1]:
            href = article["url"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)} from chinadaily fetched")
        if len(article_urls)%30 == 0 and len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        page_index += 1
    return article_urls

def get_article_url_list_for_page(newsPage: str, keyword: str = ""):
    if newsPage == "sabc":
        return get_sabc_article_urls(keyword)
    elif newsPage == "rferl":
        return get_rferl_article_urls(keyword)
    elif newsPage == "chinadaily":
        return get_chinadaily_article_urls(keyword)
    elif newsPage == "moscowtimes":
        return get_moscowtimes_article_urls(keyword)
    elif newsPage == "spiegel":
        return get_spiegel_article_urls(keyword)
    if newsPage == "cnn":
        return get_cnn_article_urls(keyword)
    if newsPage == "folha":
        return get_folha_article_urls(keyword)
    if newsPage == "tass":
        return get_tass_article_urls(keyword)
    if newsPage == "kyiv":
        return get_kyiv_article_urls(keyword)
    raise ValueError("Invalid news page entered")

def store_articles_in_file(newsPage: str, keyword: str = ""):
    links = get_article_url_list_for_page(newsPage, keyword)

    file = open(f"data/articles_{newsPage}_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()
    print(f"Found {str(len(links))} articles for {newsPage} on {keyword}.")

def is_article_too_old(url: str, date: str = "2018-01-01") -> bool:
    article = NewsPlease.from_url(url)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    
    # Extract and process dates
    if not hasattr(article, "date_publish"):
        print(f"{url} has no date_publish")
        return False
    if article.date_publish == None:
        print(f"{url} has a date_publish == none")
        return False #Returning false because otherwise we would stop getting data too early
    else:
        print(f"{str(article.date_publish)} \t<-->\t str {start_date}")
        return article.date_publish <= start_date

def start_thread(condition: bool, news_site: str, keyword: str):
    if condition:
        t = threading.Thread(group=None, target=store_articles_in_file, args=(news_site, keyword,))
        t.start()

def main():
    if not os.path.isdir(f"data"):
        os.mkdir(f"data")

    keyword = sys.argv[1]
    print(f"Looking for articles with the keyword \"{keyword}\"")
    start_thread(sabc_active, "sabc", keyword)
    start_thread(rferl_active, "rferl", keyword)
    start_thread(chinadaily_active, "chinadaily", keyword)
    start_thread(moscowtimes_active, "moscowtimes", keyword)
    start_thread(spiegel_active, "spiegel", keyword)
    start_thread(cnn_active, "cnn", keyword)
    start_thread(folha_active, "folha", keyword)
    start_thread(tass_active, "tass", keyword)
    start_thread(kyiv_active, "kyiv", keyword)
    
if __name__=="__main__":
    main()