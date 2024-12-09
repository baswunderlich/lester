#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import string
from matplotlib.pyplot import figure
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from newsplease import NewsPlease, NewsArticle
import json
import sys
import os
import hashlib
from SentimentVisualizer import plot_result, show_plots
from article_result import ArticleResult
from storable_article import StorableArticle
from scraper_thread import ScraperThread

keyword = sys.argv[1]
in_cache_mode = sys.argv.count("cache") > 0
in_offline_mode = sys.argv.count("offline") >= 1
in_rampage_mode = sys.argv.count("rampage") >= 1

sabc_active = sys.argv.count("sabc") > 0 or sys.argv.count("all") > 0
moscowtimes_active = sys.argv.count("moscowtimes") > 0 or sys.argv.count("all") > 0
rferl_active =sys.argv.count("rferl") > 0 or sys.argv.count("all") > 0
chinadaily_active =sys.argv.count("chinadaily") > 0 or sys.argv.count("all") > 0
spiegel_active = sys.argv.count("spiegel") > 0 or sys.argv.count("all") > 0
cnn_active = sys.argv.count("cnn") > 0 or sys.argv.count("all") > 0
folha_active = sys.argv.count("folha") > 0 or sys.argv.count("all") > 0

class ArticleEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

class ArticleDecoder(json.JSONDecoder):
        def default(self, o):
            return o.__dict__

def convert_to_hash(link: str) -> str:
    return hashlib.sha256(bytes(link, "utf-8")).hexdigest()

def convert_to_storable_article(old_article) -> StorableArticle:
    return StorableArticle(old_article)

def saveArticle(article, news_site, link):
    storable_article = convert_to_storable_article(article)
    article_as_json = json.dumps(storable_article, cls=ArticleEncoder)
    if not os.path.isdir(f"data/articles_{news_site}"):
        os.mkdir(f"data/articles_{news_site}")
    filename = f"data/articles_{news_site}/articles_{convert_to_hash(link)}.json"
    file = open(filename, "w")
    file.write(article_as_json)

def to_storable_result(result: [int, int], news_site: str, keyword: str, article: StorableArticle):
    result_object = ArticleResult(
        positive_result=result[0],
        negative_result=result[1],
        url=article.url,
        hash_value=convert_to_hash(article.url),
        date_publish=article.date_publish
        )
    return result_object

def saveResults(results: [[int, int]], news_site: str, keyword: str, articles: [StorableArticle]):
    file = open(f"data/results_{news_site}_{keyword}.json", "w")
    storable_result_objects = []
    for index, result in enumerate(results):
        result_object = ArticleResult(
            positive_result=result[0],
            negative_result=result[1],
            url=articles[index].url,
            hash_value=convert_to_hash(articles[index].url),
            date_publish=articles[index].date_publish
            )
        storable_result_objects.append(result_object)
    results_as_json = json.dumps(storable_result_objects, cls=ArticleEncoder)
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
def analyze_articles(articles: [StorableArticle], news_site: str, keyword: str):
    sentiment_results = []
    storable_results = []
    for i, article in enumerate(articles):
        print(f"Analyzing... {i+1}/{len(articles)} ({news_site}) -> {article.url}")
        text = ""
        if hasattr(article, "maintext"):
            text = article.maintext
        cleaned_text = clean_text(text)
        sentiment_result = sentiment_analyse(cleaned_text)
        sentiment_results.append(sentiment_result)
        storable_result = to_storable_result(
            result=sentiment_result, 
            news_site=news_site, 
            keyword=keyword, 
            article=article)
        storable_results.append(storable_result)
    saveResults(sentiment_results, news_site=news_site, keyword=keyword, articles=articles)
    return read_cached_results(news_site= news_site, keyword= keyword)

def download_article(link: str, news_site: str) -> StorableArticle:
    try:
        news_article = NewsPlease.from_url(link)
    except:
        print("Exception with: ", link)
        return None
    article = StorableArticle(news_article)
    saveArticle(article=article, news_site=news_site, link=link)
    return article

def scrap_articles(keyword: str, news_site: str) -> []:
    filename_article_hrefs = f"data/articles_{news_site}_{keyword}.txt" 
    if not os.path.isfile(filename_article_hrefs):
        print(f"No hrefs file was found for: keyword={keyword}, news_site={news_site}\n => {filename_article_hrefs}")
        return []
    article_file = open(filename_article_hrefs)
    lines = article_file.readlines()
    articles = []
    
    for i, link in enumerate(lines):
        if link == "":
            break
        link = link.strip()
        article: NewsArticle
        potential_filename = f"data/articles_{news_site}/articles_{convert_to_hash(link)}.json" 
        exists_file = os.path.isfile(potential_filename)
        if exists_file and not in_rampage_mode:
            print(f"found article {link} locally: {potential_filename} ")
            file = open(potential_filename, "r")
            article = json.loads(str(file.read()), object_hook=StorableArticle)
            if article.maintext == "":
                article = download_article(link=link, news_site=news_site)
        elif not in_offline_mode:
            article = download_article(link=link, news_site=news_site)
        else:
            print(f"There is an article missing: {link}")
            continue
        if article != None:
            if not article.maintext == "":
                articles.append(article)
                print(f"Scrapping... {i+1}/{len(lines)} ({news_site}) -> {article.url}")
    
    return articles

def read_cached_results(news_site: str, keyword: str):
    results = json.loads(open(f"data/results_{news_site}_{keyword}.json").read())
    return results

def setupNltk():
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('vader_lexicon')

def main():
    if not os.path.isdir(f"data"):
        os.mkdir(f"data")

    sabc_articles = []
    rferl_articles = []
    chinadaily_articles = []
    moscowtimes_articles = []
    spiegel_articles = []
    cnn_articles = []
    folha_articles = []

    results_sabc = []
    results_rferl = []
    results_chinadaily = []
    results_moscowtimes = []
    results_spiegel = []
    results_cnn = []
    results_folha = []

    if not in_cache_mode:    
        threads = [
            ScraperThread(program=scrap_articles, news_site="sabc", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="rferl", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="chinadaily", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="moscowtimes", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="spiegel", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="cnn", keyword=keyword),
            ScraperThread(program=scrap_articles, news_site="folha", keyword=keyword)
        ]

        if sabc_active:
            threads[0].start()
        if rferl_active:
            threads[1].start()
        if chinadaily_active:
            threads[2].start()
        if moscowtimes_active:
            threads[3].start()
        if spiegel_active:
            threads[4].start()
        if cnn_active:
            threads[5].start()
        if folha_active:
            threads[6].start()
        
        for t in threads:
            if t.is_alive():
                t.join()

        sabc_articles = threads[0].articles
        rferl_articles = threads[1].articles
        chinadaily_articles = threads[2].articles
        moscowtimes_articles = threads[3].articles
        spiegel_articles = threads[4].articles
        cnn_articles = threads[5].articles
        folha_articles = threads[6].articles

        if sabc_active:
            results_sabc = analyze_articles(sabc_articles, news_site="sabc", keyword=keyword)
        if rferl_active:
            results_rferl = analyze_articles(rferl_articles, news_site="rferl", keyword=keyword)
        if chinadaily_active:
            results_chinadaily = analyze_articles(chinadaily_articles, news_site="chinadaily", keyword=keyword)
        if moscowtimes_active:
            results_moscowtimes = analyze_articles(moscowtimes_articles, news_site="moscowtimes", keyword=keyword)
        if spiegel_active:
            results_spiegel = analyze_articles(spiegel_articles, news_site="spiegel", keyword=keyword)
        if cnn_active:
            results_cnn = analyze_articles(cnn_articles, news_site="cnn", keyword=keyword)
        if folha_active:
            results_folha = analyze_articles(folha_articles, news_site="folha", keyword=keyword)
    else:
        if sabc_active:
            results_sabc = read_cached_results(news_site="sabc", keyword=keyword)
        if rferl_active:
            results_rferl = read_cached_results(news_site="rferl", keyword=keyword)
        if chinadaily_active:
            results_chinadaily = read_cached_results(news_site="chinadaily", keyword=keyword)
        if moscowtimes_active:
            results_moscowtimes = read_cached_results(news_site="moscowtimes", keyword=keyword)
        if spiegel_active:
            results_spiegel = read_cached_results(news_site="spiegel", keyword=keyword)
        if cnn_active:
            results_cnn = read_cached_results(news_site="cnn", keyword=keyword)
        if folha_active:
            results_folha = read_cached_results(news_site="folha", keyword=keyword)

    if sabc_active:
        plot_result(results=results_sabc, news_site="sabc", keyword=keyword)
    if rferl_active:
        plot_result(results=results_rferl, news_site="rferl", keyword=keyword)
    if chinadaily_active:
        plot_result(results=results_chinadaily, news_site="chinadaily", keyword=keyword)
    if moscowtimes_active:
        plot_result(results=results_moscowtimes, news_site="moscowtimes", keyword=keyword)
    if spiegel_active:
        plot_result(results=results_spiegel, news_site="spiegel", keyword=keyword)
    if cnn_active:
        plot_result(results=results_cnn, news_site="cnn", keyword=keyword)
    if folha_active:
        plot_result(results=results_folha, news_site="folha", keyword=keyword)
    show_plots(keyword=keyword)

if __name__=="__main__":
    setupNltk()
    main()