import json
import requests


def get_secret(name: str) -> str:
    secrets = json.loads(open("secrets.json", "r").read())
    return secrets[name]

def get_articles_urls(news_api_response: str) -> [str]:
    article_urls = []
    response = json.loads(news_api_response)
    for a in response["articles"]:
        article_urls.append(a["url"])
    return article_urls

API_KEY = get_secret("news_api_key")

keyword = "climate"
url = f"GET https://newsapi.org/v2/top-headlines/sources?category=businessapiKey={API_KEY}"
print(url)
response = requests.get(url)
print(response)
articles = get_articles_urls(response.text)
print(len(articles))