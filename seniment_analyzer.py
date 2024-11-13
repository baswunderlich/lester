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
from newsplease import NewsPlease
import matplotlib.pyplot as plt
import json
import sys
import os

#necessary due to the fact, that NewsArticle can not be serialized as json
class StorableArticle:
    maintext: str
    source_domain: str
    title: str
    url: str
    description: str
    date_publish: str
    date_download: str

    def __init__(self, old_article):
        self.maintext = old_article.maintext
        self.source_domain = old_article.source_domain
        self.title = old_article.title
        self.url = old_article.url
        self.description = old_article.description
        self.date_publish = str(old_article.date_publish)
        self.date_download = str(old_article.date_download)


    # def serialize(self):
    #     return {"maintext": self.maintext,
    #             "source_domain": self.source_domain,
    #             "title": self.title,
    #             "url": self.url,
    #             "description": self.description}


# subclass JSONEncoder
class ArticleEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

def convert_to_storable_article(
    old_article) -> StorableArticle:
    return StorableArticle(old_article)

def saveArticle(article, newssite, link):
    storable_article = convert_to_storable_article(article)
    article_as_json = json.dumps(storable_article, cls=ArticleEncoder)
    if not os.path.isdir(f"articles_{newssite}"):
        os.mkdir(f"articles_{newssite}")
    filename = f"articles_{newssite}/articles_{str(hash(link))}.json"
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
    tokenized_words = word_tokenize(cleaned_text, "german")

    # Removing Stop Words
    final_words = []
    for word in tokenized_words:
        if word not in stopwords.words('german'):
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

def scrap_articles(filename: str) -> []:
    file = open(filename)
    lines = file.readlines()
    articles = []
    for i, line in enumerate(lines):
        article: NewsArticle
        if os.path.isfile(f"articles_sabc/articles_{str(hash(line))}"):
            article = NewsPlease.from_file(f"articles_sabc/articles_{str(hash(line))}.json")
        else:
            article = NewsPlease.from_url(line)
        articles.append(article)
        saveArticle(article=article, newssite=filename.split("_")[0], link=line)
        print(f"Scrapping... {i}/{len(lines)}")
    return articles

#This function analyzes the articles in the "sabc_articles.txt" file
def analyze_sabc_articles() -> []:
    sabc_articles = scrap_articles("sabc_articles.txt")
    results = analyze_articles(sabc_articles)
    saveResults(results)
    return results

def plot_result(results):
    x = np.array(range(0,len(results)))
    #positive
    y1 = np.array(results).T[0]
    plt.title("plotting the sentiment of SABC")
    coef1 = np.polyfit(x,y1,1)
    pos_fn = np.poly1d(coef1) 
    #negative
    #The difference between the positive and the negative value
    y2 = np.array(results).T[1]
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    coef2 = np.polyfit(x,y2,1)
    neg_fn = np.poly1d(coef2) 
    plt.plot(x,y1,x,y2)
    plt.plot(pos_fn(x), '--k', color="#0e7800")
    plt.plot(neg_fn(x), "--k", color="#ed1103")
    plt.show()


    #The difference between the positive and the negative value
    y = np.array(results).T[0] - np.array(results).T[1]
    coef = np.polyfit(x,y,1)
    poly1d_fn = np.poly1d(coef) 
    plt.plot(x,y, 'yo', x, poly1d_fn(x), '--k')
    plt.show()

def main():
    results = []
    if sys.argv.count("offline") == 0:
        results = analyze_sabc_articles()
    else:
        json_results = open("results.json", "r")
        results = json.load(json_results)
    plot_result(results=results)

if __name__=="__main__":
    main()