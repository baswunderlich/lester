import requests
from bs4 import BeautifulSoup
import sys
import threading
import json

def get_spiegel_article_urls(limit: int, keyword: str) -> []:
    article_urls = []
    page_index = 2

    while True:
        url = f"https://www.spiegel.de/services/sitesearch/search?segments=spon_international&q={keyword}&after=-2208988800&before=1733078189&page_size=20&page={page_index}"
        response = json.loads(requests.get(url).text)
        results = response["results"]

        for r in results:
            href = r["url"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)}/{limit}")
            if len(article_urls) >= limit:
                return article_urls
        page_index += 1

def get_moscowtimes_article_urls(limit: int, keyword: str) -> []:
    article_urls = []
    pageindex = 1

    url = f"https://www.themoscowtimes.com/api/search?query={keyword}&section=news"
    response = json.loads(requests.get(url).text)
    for i in range(min(len(response), limit)):
        article_urls.append(response[i]["url"])
    return article_urls

def get_sabc_article_urls(limit: int, keyword: str) -> []:
    article_urls = []
    pageindex = 1

    while True:
        url = f"https://www.sabcnews.com/sabcnews/page/{pageindex}/?s={keyword}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("article")
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                href = a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)}/{limit}")
                if len(article_urls) >= limit:
                    return article_urls
        pageindex += 1

def get_rferl_article_urls(limit: int, keyword: str):
    article_urls = []
    pageindex = 1

    while len(article_urls) < limit:
        url = f"https://www.rferl.org/s?k={keyword}&tab=news&pi={pageindex}&r=any&pp=50"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("div", {"class": "media-block"})
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                #At this site. The hrefs do not include the serveradresse.
                #Therefore it needs to be added
                href = "https://www.rferl.org" + a["href"]
                if article_urls.count(href) == 0:
                    article_urls.append(href)
                    print(f"{len(article_urls)}/{limit}")
                if len(article_urls) >= limit:
                    return article_urls
        pageindex += 1

def get_chinadaily_article_urls(limit: int, keyword: str):
    article_urls = []
    #Chinadaily starts with the pageIndex 0
    pageindex = 0

    while len(article_urls) < limit:
        url = f"https://newssearch.chinadaily.com.cn/rest/en/search?keywords={keyword}&sort=dp&page={pageindex}&curType=story&type=&channel=&source="
        page = requests.get(url)
        page_decoded = json.loads(page.text)

        for article in page_decoded["content"]:
            href = article["url"]
            if article_urls.count(href) == 0:
                article_urls.append(href)
                print(f"{len(article_urls)}/{limit}")
            if len(article_urls) >= limit:
                return article_urls
        pageindex += 1

def get_article_url_list_for_page(newsPage: str, amount: int = 500, keyword: str = ""):
    if newsPage == "sabc":
        return get_sabc_article_urls(amount, keyword)
    elif newsPage == "rferl":
        return get_rferl_article_urls(amount, keyword)
    elif newsPage == "chinadaily":
        return get_chinadaily_article_urls(amount, keyword)
    elif newsPage == "moscowtimes":
        return get_moscowtimes_article_urls(amount, keyword)
    elif newsPage == "spiegel":
        return get_spiegel_article_urls(amount, keyword)
    raise ValueError("Invalid news page entered")

def store_articles_in_file(newsPage: str, amount: int = 500, keyword: str = ""):
    links = get_article_url_list_for_page(newsPage, amount, keyword)

    file = open(f"articles_{newsPage}_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()


def main():
    keyword = sys.argv[1]
    amount = int(sys.argv[2])
    print(f"Looking for articles with the keyword \"{keyword}\"")

    t1 = threading.Thread(group=None, target=store_articles_in_file, args=("sabc", amount, keyword,))
    t2 = threading.Thread(group=None, target=store_articles_in_file, args=("rferl", amount, keyword,))
    t3 = threading.Thread(group=None, target=store_articles_in_file, args=("chinadaily", amount, keyword,))
    t4 = threading.Thread(group=None, target=store_articles_in_file, args=("moscowtimes", amount, keyword,))
    t5 = threading.Thread(group=None, target=store_articles_in_file, args=("spiegel", amount, keyword,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    
if __name__=="__main__":
    main()