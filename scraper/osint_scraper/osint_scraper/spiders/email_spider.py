import scrapy

class EmailSpider(scrapy.Spider):
    name = "email_lookup"
    allowed_domains = ["google.com"]
    # dynamically set in CLI: -a email=someone@example.com
    start_urls = []

    def __init__(self, email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if email:
            query = f'"{email}" site:linkedin.com OR site:github.com OR site:twitter.com'
            self.start_urls = [f"https://www.google.com/search?q={query}"]

    def parse(self, response):
        for result in response.css("a::attr(href)").getall():
            yield {"link": result}

