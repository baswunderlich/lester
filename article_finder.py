import requests
from bs4 import BeautifulSoup


def get_article_urls(limit: int, keyword: str) -> []:
    article_urls = []
    pageindex = 1

    while len(article_urls) < limit:
        url = f"https://www.sabcnews.com/sabcnews/page/{pageindex}/?s={keyword}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        articles = soup.find_all("article")
        for article in articles:
            a_s = article.find_all("a")
            for a in a_s:
                href = a["href"]
                article_urls.append(href)
        pageindex += 1
    return article_urls




links = get_article_urls(500, "trump")
for link in links:
    if links.count(link) > 1:
        links.remove(link)

file = open("sabc_articles.txt", "w")
for link in links:
    file.write(link+"\n")
file.close()
