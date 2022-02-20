import scrapy
from scrapy import Selector
from selenium import webdriver
import selenium.common.exceptions as exception
import json
import time



class UrlsSpiderSpider(scrapy.Spider):

    name = "urls_spider"
    allowed_domains = ["emlak.az"]

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://emlak.az"
        yield scrapy.Request(url=url, callback=self.parse_urls)

    def parse_urls(self, response):
        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        driver.get("http://emlak.az")

        selenium_response_text = driver.page_source
        selector = Selector(text=selenium_response_text)
        urls = selector.xpath('//a[contains(@class,"more")]/@href').getall()

        #print(urls)
        
        yield {
            'urls': urls,
        }

        """for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }"""

        """def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')


        def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)"""

        driver.quit()
