class ArticleResult:
    positive_result: int
    negative_result: int
    url: str
    hash_value: str
    date_published: str

    def __init__(self, 
        positive_result: int,
        negative_result: int, 
        url: str, 
        hash_value: str, 
        date_published: str):

        self.positive_result = positive_result
        self.negative_result = negative_result
        self.url = url
        self.hash_value = hash_value
        if(len(date_published) >= 10):
            self.date_published = date_published

    
    def to_dict(self):
        return {
            "positive_result": self.positive_result,
            "negative_result": self.negative_result,
            "url": self.url,
            "hash_value": self.hash_value
        }