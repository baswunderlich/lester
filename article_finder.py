import requests
from bs4 import BeautifulSoup
import sys
import threading
import json
import os 
from newsplease import NewsArticle, NewsPlease
import datetime

sabc_active = sys.argv.count("sabc") > 0 or sys.argv.count("all") > 0
moscowtimes_active = sys.argv.count("moscowtimes") > 0 or sys.argv.count("all") > 0
rferl_active =sys.argv.count("rferl") > 0 or sys.argv.count("all") > 0
chinadaily_active =sys.argv.count("chinadaily") > 0 or sys.argv.count("all") > 0
spiegel_active = sys.argv.count("spiegel") > 0 or sys.argv.count("all") > 0
sydney_active = sys.argv.count("sydney") > 0 or sys.argv.count("all") > 0


def get_sydneyMH_article_urls(keyword: str) -> list:  # Sydney Morning Herald
    article_urls = []
    page_index = 1
    enough_articles = False

    while not enough_articles:
        url = f"https://www.smh.com.au/search?sortBy=MOST_RECENT&text={keyword}&page={page_index}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Locate sections with the class `_1h0gt`
        sections = soup.find_all("section", class_="_1H0gt")
        print(f"Found {len(sections)} sections on page {page_index}.")  # Debug print
        
        for section in sections:
            # Locate individual article divs within the section
            article_divs = section.find_all("div", attrs={"data-testid": "index-story-tile"})
            
            for article_div in article_divs:
                # Extract <a> tags with the desired link
                link_tag = article_div.find("a", attrs={"data-testid": "article-link"})
                if link_tag:
                    href = f'https://www.smh.com.au{link_tag["href"]}'
                    # Avoid duplicates
                    if href not in article_urls:
                        article_urls.append(href)
                        print(f"{len(article_urls)} articles fetched")
        
        # Check if we've collected enough articles or reached old ones
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):  # Replace this function with your logic
                enough_articles = True
        
        page_index += 1
    
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
    pageindex = 1

    url = f"https://www.themoscowtimes.com/api/search?query={keyword}&section=news"
    response = json.loads(requests.get(url).text)
    for i in range(min(len(response), 300)):
        href = response[i]["url"]
        article_urls.append(href)
    return article_urls

def get_sabc_article_urls(keyword: str) -> []:
    article_urls = []
    pageindex = 1
    enough_articles = False

    while not enough_articles:
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
                    print(f"{len(article_urls)} articles from SABC fetched")
        if len(article_urls) > 0:
            if is_article_too_old(article_urls[-1]):
                enough_articles = True
        pageindex += 1
    return article_urls

def get_rferl_article_urls(keyword: str):
    article_urls = []
    pageindex = 1
    enough_articles = False
    
    while not enough_articles:
        url = f"https://www.rferl.org/s?k={keyword}&tab=news&pi={pageindex}&r=any&pp=50"
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
        pageindex += 1
    return article_urls

def get_chinadaily_article_urls(keyword: str):
    article_urls = []
    #Chinadaily starts with the pageIndex 0
    pageindex = 0
    enough_articles = False

    while not enough_articles:
        #Using chindailys advanced search
        # url = f"https://newssearch.chinadaily.com.cn/rest/en/search?publishedDateFrom=2018-01-01&publishedDateTo=2024-12-05&fullMust=climate&channel=&type=&curType=story&sort=dp&duplication=on&page=0&type[0]=story&channel[0]=2@cndy&source="
        url = f"https://newssearch.chinadaily.com.cn/rest/en/search?keywords={keyword}&sort=dp&page={pageindex}&curType=story&type=&channel=&source="
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
        pageindex += 1
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
    elif newsPage == "sydney":
        return get_sydneyMH_article_urls(keyword)
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
    print(f"{str(article.date_publish)} \t<-->\t str {start_date}")
    if article.date_publish == None:
        return False #Returning false because otherwise we would stop getting data too early
    else:
        return article.date_publish <= start_date

def main():
    if not os.path.isdir(f"data"):
        os.mkdir(f"data")

    keyword = sys.argv[1]
    print(f"Looking for articles with the keyword \"{keyword}\"")
    if sydney_active:
        t6 = threading.Thread(group=None, target=store_articles_in_file, args=("sydney", keyword,))
        t6.start()
    # if sabc_active:
    #     t1 = threading.Thread(group=None, target=store_articles_in_file, args=("sabc", keyword,))
    #     t1.start()
    # if rferl_active:
    #     t2 = threading.Thread(group=None, target=store_articles_in_file, args=("rferl", keyword,))
    #     t2.start()
    # if chinadaily_active:
    #     t3 = threading.Thread(group=None, target=store_articles_in_file, args=("chinadaily", keyword,))
    #     t3.start()
    # if moscowtimes_active:
    #     t4 = threading.Thread(group=None, target=store_articles_in_file, args=("moscowtimes", keyword,))
    #     t4.start()
    # if spiegel_active:
    #     t5 = threading.Thread(group=None, target=store_articles_in_file, args=("spiegel", keyword,))
    #     t5.start()

    
if __name__=="__main__":
    main()