# custom thread
from threading import Thread

class ScraperThread(Thread):
    def __init__(self, program, news_site, keyword):
        self.program = program
        self.articles = []
        self.news_site = news_site
        self.keyword = keyword
        Thread.__init__(self)

    def run(self):
	    self.articles = self.program(keyword=self.keyword, news_site=self.news_site)