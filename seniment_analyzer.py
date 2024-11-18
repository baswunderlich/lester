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


# custom thread
class AnalyzerThread(Thread):
    def __init__(self, program, keyword):
        self.program = program
        self.results = []
        self.keyword = keyword
        Thread.__init__(self)


    def run(self):
	    self.results = self.program(self.keyword)

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

def saveArticle(article, newssite, link):
    storable_article = convert_to_storable_article(article)
    article_as_json = json.dumps(storable_article, cls=ArticleEncoder)
    if not os.path.isdir(f"articles_{newssite}"):
        os.mkdir(f"articles_{newssite}")
    filename = f"articles_{newssite}/articles_{convert_to_hash(link)}.json"
    file = open(filename, "w")
    file.write(article_as_json)

def saveResults(results, newssite):
    file = open(f"results_{newssite}.json", "w")
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
    for word in tokenized_words:
        if word not in stopwords.words():
            final_words.append(word)

    # Lemmatization - From plural to single + Base form of a word (example better-> good)
    lemma_words = []
    for word in final_words:
        word = WordNetLemmatizer().lemmatize(word)
        lemma_words.append(word)

    emotion_list = []
    with open('emotions.txt', 'r') as file:
        for line in file:
            clear_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
            word, emotion = clear_line.split(':')

            if word in lemma_words:
                emotion_list.append(emotion)
                
    return cleaned_text

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
def analyze_articles(articles) -> [[int]]:
    sentiment_results = []
    for i, article in enumerate(articles):
        text = ""
        if hasattr(article, "maintext"):
            text = article.maintext
        cleaned_text = clean_text(text)
        sentiment_results.append(sentiment_analyse(cleaned_text))
        print(f"Analyzing... {i}/{len(articles)}")
    return sentiment_results

def download_article(link: str, newssite: str) -> NewsArticle:
    article = StorableArticle(NewsPlease.from_url(link))
    saveArticle(article=article, newssite=newssite, link=link)
    return article

def scrap_articles(keyword: str, newssite: str) -> []:
    filename_article_hrefs = f"articles_{newssite}_{keyword}.txt"
    if os.path.isfile(filename_article_hrefs):
        file = open(filename_article_hrefs)
    else:
        print(f"No hrefs file was found for: keyword={keyword}, newssite={newssite}\n => {filename_article_hrefs}")
        return []    
    lines = file.readlines()
    articles = []
    for i, link in enumerate(lines):
        if link == "":
            break
        link = link.strip()
        article: NewsArticle
        potential_filename = f"articles_{newssite}/articles_{convert_to_hash(link)}.json" 
        exists_file = os.path.isfile(potential_filename)
        in_offline_mode = sys.argv.count("offline") >= 1
        if exists_file and in_offline_mode:
            print(f"found {potential_filename} in cache")
            file = open(potential_filename, "r")
            article = json.loads(str(file.read()), object_hook=StorableArticle)
            if article.maintext == "":
                article = download_article(link=link, newssite=newssite)
        else:
            article = download_article(link=link, newssite=newssite)
        if article.maintext == "":
            continue
        articles.append(article)
        print(f"Scrapping... {i}/{len(lines)}")
    return articles

def analyze_sabc_articles(keyword: str) -> []:
    sabc_articles = scrap_articles(keyword=keyword, newssite="sabc")
    results = analyze_articles(sabc_articles)
    saveResults(results, "sabc")
    return results
    
def analyze_rferl_articles(keyword: str) -> []:
    sabc_articles = scrap_articles(keyword=keyword, newssite="rferl")
    results = analyze_articles(sabc_articles)
    saveResults(results, "rferl")
    return results

def plot_result(results, newssite):
    x = np.array(range(0,len(results)))
    #positive
    y1 = np.array(results).T[0]
    plt.title(f"plotting the sentiment of {newssite}")
    coef1 = np.polyfit(x,y1,1)
    pos_fn = np.poly1d(coef1) 
    #negative
    #The difference between the positive and the negative value
    y2 = np.array(results).T[1]
    coef2 = np.polyfit(x,y2,1)
    neg_fn = np.poly1d(coef2) 
    plt.plot(x,y1,x,y2)
    plt.plot(pos_fn(x), color="#0e7800", linestyle="dashed")
    plt.plot(neg_fn(x), color="#ed1103", linestyle="dashed")
    plt.show()


    #The difference between the positive and the negative value
    y = np.array(results).T[0] - np.array(results).T[1]
    coef = np.polyfit(x,y,1)
    poly1d_fn = np.poly1d(coef) 
    plt.plot(x,y, 'yo', x, poly1d_fn(x), '--k')
    plt.show()

def generate_results_sabc(keyword: str):
    results = []
    use_cache = sys.argv.count("cache") > 0
    if use_cache:
        results = json.loads(open(f"results_sabc_{keyword}.json").read())
    else:
        results = analyze_sabc_articles(keyword=keyword)
    return results

def generate_results_rferl(keyword: str):
    results = []
    use_cache = sys.argv.count("cache") > 0
    if use_cache:
        results = json.loads(open(f"results_rferl_{keyword}.json").read())
    else:
        results = analyze_rferl_articles(keyword=keyword)
    return results

def main():
    keyword = sys.argv[1]

    t1 = AnalyzerThread(program=generate_results_sabc, keyword=keyword)
    t2 = AnalyzerThread(program=generate_results_rferl, keyword=keyword)

    if sys.argv.count("sabc") > 0 or sys.argv.count("all") > 0:
        t1.start()
    if sys.argv.count("rferl") > 0 or sys.argv.count("all") > 0:
        t2.start()
    
    t1.join()
    t2.join()
    
    results_sabc = t1.results
    results_rferl = t2.results

    print(results_sabc)
    print(results_rferl)

    plot_result(results=results_sabc, newssite="sabc")
    plot_result(results=results_rferl, newssite="rferl")

if __name__=="__main__":
    main()