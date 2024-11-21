import requests
from bs4 import BeautifulSoup
import sys
import threading
import json

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

def find_sabc_articles(amount: int = 500, keyword: str = ""):
    links = get_sabc_article_urls(amount, keyword=keyword)

    file = open(f"articles_sabc_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()

def find_rferl_articles(amount: int = 500, keyword: str = ""):
    links = get_rferl_article_urls(amount, keyword=keyword)

    file = open(f"articles_rferl_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()

def find_chinadaily_articles(amount: int = 500, keyword: str = ""):
    links = get_chinadaily_article_urls(amount, keyword=keyword)

    file = open(f"articles_chinadaily_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()
def getArticleUrlListForPage(newsPage: str, amount: int = 500, keyword: str = ""):
    if newsPage == "sabc":
        return get_sabc_article_urls(amount, keyword)
    elif newsPage == "rferl":
        return get_rferl_article_urls(amount, keyword)
    raise ValueError("Invlaid news page entered")

def storeArticlesInFile(newsPage: str, amount: int = 500, keyword: str = ""):
    links = getArticleUrlListForPage(newsPage)

    file = open(f"articles_{newsPage}_{keyword}.txt", "w")
    for link in links:
        file.write(link+"\n")
    file.close()


def main():
    keyword = sys.argv[1]
    amount = int(sys.argv[2])
    print(f"Looking for articles with the keyword \"{keyword}\"")

    # t1 = threading.Thread(group=None, target=find_sabc_articles, args=(amount, keyword,))
    # t2 = threading.Thread(group=None, target=find_rferl_articles, args=(amount, keyword,))
    t3 = threading.Thread(group=None, target=find_chinadaily_articles, args=(amount, keyword,))

    # t1.start()
    # t2.start()
    t3.start()
    
if __name__=="__main__":
    main()