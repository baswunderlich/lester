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

def saveResults(results):
    file = open("results.json", "w")
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
def analyze(articles) -> [[int]]:
    sentiment_results = []
    for i, article in enumerate(articles):
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
        article = NewsPlease.from_url(line)
        articles.append(article)
        print(f"Scrapping... {i}/{len(lines)}")
    return articles

#This function analyzes the articles in the "sabc_articles.txt" file
def analyze_sabc_articles() -> []:
    sabc_articles = scrap_articles("sabc_articles.txt")
    results = analyze(sabc_articles)
    saveResults(results)
    return results

def plot_result(results):
    x = np.array(range(0,len(results)))
    #positive
    y = np.array(results).T[0]
    plt.title("plotting the sentiment of SABC")
    for i, array in enumerate(y):
        plt.plot(
            x[i],
            array,
            color="#0e7800",
            marker="."
        )
    #negative
    y = np.array(results).T[1]
    for i, array in enumerate(y):
        plt.plot(
            x[i],
            array,
            color="#ed1103",
            marker="."
        )
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.show()

    #The difference between the positive and the negative value
    y = np.array(results).T[0] - np.array(results).T[1]
    coef = np.polyfit(x,y,1)
    poly1d_fn = np.poly1d(coef) 
    # poly1d_fn is now a function which takes in x and returns an estimate for y

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