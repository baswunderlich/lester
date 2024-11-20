#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import string
from collections import Counter
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import numpy as np
import newsplease
from newsplease import NewsPlease, NewsArticle
import matplotlib.pyplot as plt
import json
import sys
import os
import hashlib
from threading import Thread


in_offline_mode = sys.argv.count("offline") >= 1
in_rampage_mode = sys.argv.count("rampage") >= 1

# custom thread
class ScraperThread(Thread):
    def __init__(self, program, news_site, keyword):
        self.program = program
        self.articles = []
        self.news_site = news_site
        self.keyword = keyword
        Thread.__init__(self)


    def run(self):
	    self.articles = self.program(keyword=self.keyword, news_site=self.news_site)

#necessary due to the fact, that NewsArticle can not be serialized as json
class StorableArticle:
    maintext: str = ""
    source_domain: str = ""
    title: str = ""
    url: str = ""
    description: str = ""
    date_publish: str = ""
    date_download: str = ""

    def __init__(self, old_article):
        if isinstance(old_article, dict):
            self.__dict__.update(old_article)
        else:
            self.maintext = old_article.maintext
            self.source_domain = old_article.source_domain
            self.title = old_article.title
            self.url = old_article.url
            self.description = old_article.description
            self.date_publish = str(old_article.date_publish)
            self.date_download = str(old_article.date_download)

class ArticleEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

class ArticleDecoder(json.JSONDecoder):
        def default(self, o):
            return o.__dict__

def convert_to_hash(link: str) -> str:
    return hashlib.sha256(bytes(link, "utf-8")).hexdigest()

def convert_to_storable_article(
    old_article) -> StorableArticle:
    return StorableArticle(old_article)

def saveArticle(article, news_site, link):
    storable_article = convert_to_storable_article(article)
    article_as_json = json.dumps(storable_article, cls=ArticleEncoder)
    if not os.path.isdir(f"articles_{news_site}"):
        os.mkdir(f"articles_{news_site}")
    filename = f"articles_{news_site}/articles_{convert_to_hash(link)}.json"
    file = open(filename, "w")
    file.write(article_as_json)

def saveResults(results, news_site, keyword):
    file = open(f"results_{news_site}_{keyword}.json", "w")
    results_as_json = json.dumps(results)
    file.write(results_as_json)

def clean_text(text) -> str:
    if text is None:
        return ""

    lower_case = text.lower()
    cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))

    # Using word_tokenize because it's faster than split()
    tokenized_words = word_tokenize(cleaned_text)

    # Removing Stop Words
    final_words = []
    stop_words = stopwords.words('english')
    legalStopwords = ["no", "not"]
    stop_words = [stopWord for stopWord in stop_words if stopWord not in legalStopwords]
    # print(stop_words)
    for word in tokenized_words:
        if word not in stop_words:
            final_words.append(word)

    # Lemmatization - From plural to single + Base form of a word (example better-> good)
    lemma_words = []
    for word in final_words:
        word = WordNetLemmatizer().lemmatize(word)
        lemma_words.append(word)
                
    return " ".join(lemma_words)

#This function returns a tuple. 
# [0]: The positive value 
# [1]: The negative value.
def sentiment_analyse(sentiment_text) -> [int]:
    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
    result = [score["pos"], score["neg"]]
    if len(result) < 2:
        return [0,0]
    return result

#This function returns a list of tuples. Every tuple contains the following:
# [0]: The positive value 
# [1]: The negative value.
def analyze_articles(articles: [StorableArticle], news_site: str, keyword: str) -> [[int]]:
    sentiment_results = []
    for i, article in enumerate(articles):
        text = ""
        if hasattr(article, "maintext"):
            text = article.maintext
        cleaned_text = clean_text(text)
        sentiment_result = sentiment_analyse(cleaned_text)
        sentiment_results.append(sentiment_result)
        print(f"Analyzing... {i+1}/{len(articles)} ({news_site}) -> {article.url}")
    saveResults(sentiment_results, news_site=news_site, keyword=keyword)
    return sentiment_results

def download_article(link: str, news_site: str) -> StorableArticle:
    article = StorableArticle(NewsPlease.from_url(link))
    saveArticle(article=article, news_site=news_site, link=link)
    return article

def scrap_articles(keyword: str, news_site: str) -> []:   
    article_file = open(f"articles_{news_site}_{keyword}.txt")
    filename_article_hrefs = f"articles_{news_site}_{keyword}.txt" 
    lines = article_file.readlines()
    articles = []
    for i, link in enumerate(lines):
        if link == "":
            break
        link = link.strip()
        article: NewsArticle
        potential_filename = f"articles_{news_site}/articles_{convert_to_hash(link)}.json" 
        exists_file = os.path.isfile(potential_filename)
        if exists_file and not in_rampage_mode:
            if os.path.isfile(filename_article_hrefs):
                file = open(filename_article_hrefs)
            else:
                print(f"No hrefs file was found for: keyword={keyword}, news_site={news_site}\n => {filename_article_hrefs}")
                return []
            print(f"found article {link} locally: {potential_filename} ")
            file = open(potential_filename, "r")
            article = json.loads(str(file.read()), object_hook=StorableArticle)
            if article.maintext == "":
                article = download_article(link=link, news_site=news_site)
        elif not in_offline_mode:
            article = download_article(link=link, news_site=news_site)
        if article.maintext == "":
            continue
        articles.append(article)
        print(f"Scrapping... {i+1}/{len(lines)} ({news_site}) -> {article.url}")
    return articles

def scrap_sabc_articles(keyword: str) -> []:
    sabc_articles = scrap_articles(keyword=keyword, news_site="sabc")
    return sabc_articles

def scrap_rferl_articles(keyword: str) -> []:
    rferl_articles = scrap_articles(keyword=keyword, news_site="rferl")
    return rferl_articles

def plot_result(results, news_site):
    x = np.array(range(0,len(results)))
    #positive
    y1 = np.array(results).T[0]
    plt.title(f"plotting the sentiment of {news_site}")
    coef1 = np.polyfit(x,y1,1)
    pos_fn = np.poly1d(coef1) 
    #negative
    #The difference between the positive and the negative value
    y2 = np.array(results).T[1]
    coef2 = np.polyfit(x,y2,1)
    neg_fn = np.poly1d(coef2) 
    plt.plot(x,y1,x,y2)
    plt.plot(pos_fn(x), color="#0e7800", linestyle="dashed") #positive is blue
    plt.plot(neg_fn(x), color="#ed1103", linestyle="dashed") #negative is red
    plt.show()


    #The difference between the positive and the negative value
    y = np.array(results).T[0] - np.array(results).T[1]
    coef = np.polyfit(x,y,1)
    poly1d_fn = np.poly1d(coef) 
    plt.plot(x,y, 'yo', x, poly1d_fn(x), '--k')
    plt.show()

def read_cached_results(news_site: str, keyword: str):
    results = json.loads(open(f"results_{news_site}_{keyword}.json").read())
    return results

def main():
    keyword = sys.argv[1]
    cached = sys.argv.count("cache") > 0

    sabc_articles = []
    rferl_articles = []

    sabc_active = sys.argv.count("sabc") > 0 or sys.argv.count("all") > 0
    rferl_active =sys.argv.count("rferl") > 0 or sys.argv.count("all") > 0

    threads = [
        ScraperThread(program=scrap_articles, news_site="sabc", keyword=keyword),
        ScraperThread(program=scrap_articles, news_site="rferl", keyword=keyword)
    ]

    if not cached:    
        if sabc_active:
            threads[0].start()
        if rferl_active:
            threads[1].start()
        
        for t in threads:
            if t.is_alive():
                t.join()

        sabc_articles = threads[0].articles
        rferl_articles = threads[1].articles

        if sabc_active:
            results_sabc = analyze_articles(sabc_articles, news_site="sabc", keyword=keyword)
        if rferl_active:
            results_rferl = analyze_articles(rferl_articles, news_site="rferl", keyword=keyword)
    else:
        if sabc_active:
            results_sabc = read_cached_results(news_site="sabc", keyword=keyword)
        if rferl_active:
            results_rferl = read_cached_results(news_site="rferl", keyword=keyword)

    if sabc_active:
        plot_result(results=results_sabc, news_site="sabc")
    if rferl_active:
        plot_result(results=results_rferl, news_site="rferl")

if __name__=="__main__":
    main()