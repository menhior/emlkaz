import scrapy
from scrapy import Selector
from selenium import webdriver
import selenium.common.exceptions as exception
import json
import time
from webdriver_manager.chrome import ChromeDriverManager


class UrlsSpiderSpider(scrapy.Spider):

    name = "ticket_urls_spider"
    allowed_domains = ["emlak.az"]
    page_number = 2

    # Using a dummy website to start scrapy request
    def start_requests(self):
        #url = "http://emlak.az"

        with open("house_type_urls.json", "r") as f:
            temp_list = json.load(f)

        urls = temp_list[0]['urls']

        elanlar = "elanlar"

        original_url = "http://emlak.az"
        page_url = "&sort_type=0&page=1&page=0"

        clean_urls = [ele for ele in urls if( elanlar in ele)]
        full_clean_urls = [original_url + ele + page_url for ele in clean_urls]

        url = full_clean_urls[0]
        #for url in full_clean_urls:            
        yield scrapy.Request(url=url, callback=self.parse_urls)

    def parse_urls(self, response):
        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        options.add_argument("--remote-debugging-port=9222")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        current_url = response.url

        driver.get(current_url)
        driver.implicitly_wait(10)
        selenium_response_text = driver.page_source
        selector = Selector(text=selenium_response_text)
        
        tickets = selector.xpath('//div[@class="ticket clearfix pinned"]')
        for ticket in tickets: 
            ticket_link = ticket.xpath(".//a/@href")
            yield from response.follow_all(ticket_link, self.parse_ticket)


        pagination_numbers = response.xpath('//div[@class="pagination"]/ul/li/a/text()').getall()
        pagination_numbers = set(pagination_numbers)
        pagination_numbers = list(pagination_numbers)
        pagination_numbers.sort()

        driver.quit()

        page_len = 70

        numbers_to_take_off = len(current_url) - page_len + 1
        next_page_number = str(int(current_url[-numbers_to_take_off:]) + 1)
        b=current_url[:-numbers_to_take_off] + next_page_number
        #print('YOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        if 'Növbəti → ' in pagination_numbers and int(current_url[-numbers_to_take_off:]) !=2:
            time.sleep(10)
            yield response.follow(url=b, callback=self.parse_urls)
        else:
            print('Finished')


    def parse_ticket(self, response):

        title = response.xpath('//h1[@class="title"]/text()').extract()
        page_title = response.xpath('//title/text()').get()
        description = response.xpath('//div[@class="desc"]/p/text()').get()
        map_address = response.xpath('//div[@class="map-address"]/h4/text()').get()       
        map_coordinates = response.css('div.map-address div#show_map_google input::attr(value)').get()
        date = response.xpath('//span[@class="date"]/strong/text()').get()
        house_price_azn = response.xpath('//div[@class="price"]/span[@class="m"]/text()').get()
        house_price_usd = response.xpath('//div[@class="price"]/span[@class="d"]/text()').get()
        house_data_labels = response.xpath('//dl[@class="technical-characteristics"]/dd/span[@class="label"]/text()').getall()
        house_data = response.xpath('//dl[@class="technical-characteristics"]/dd/text()').getall()
        user_name = response.xpath('//div[@class="seller-data clearfix"]/div[@class="silver-box"]/p[@class="name-seller"]/text()').get()
        user_phone = response.xpath('//div[@class="seller-data clearfix"]/div[@class="silver-box"]/p[@class="phone"]/text()').get()

        print(title)
        print(page_title)
        print(description)

        yield {
            'title': title,
            'page_title': page_title,
            'description': description,
            'house_price_azn': house_price_azn,
            'house_price_usd' : house_price_usd,
            'house_data_labels': house_data_labels,
            'house_data': house_data,
            'name': user_name,
            'phone': user_phone,
            'map_address': map_address,
            'map_coordinates': map_coordinates,
            'date': date,
        }



        """def extract_with_xpath(query):
            print('yessssssssss')"""
        """def extract_with_css(query):
            return response.css(query).get(default='').strip()

        
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }"""