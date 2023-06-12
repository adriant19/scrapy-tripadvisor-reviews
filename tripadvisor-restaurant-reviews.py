import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from random import randint
import time


class ReviewSpider(scrapy.Spider):
    """ TripAdvisor Restaurant Reviews Crawler

    restaurant  : name of restaurant
    review_id   : unique identifier of tripadvisor review
    date        : date of review
    stay_date   : date of reviewer's visit
    user        : name of reviewer
    badge       : count of reviews given by user
    rating      : rating given
    title       : title of review
    review      : content of review
    """

    name = "tripadvisor-reviews"

    allowed_domains = ["tripadvisor.com.my"]

    start_urls = [  # list of pages to scrape
        "https://www.tripadvisor.com.my/Restaurant_Review-g298313-d4915935-Reviews-Kampachi_Plaza33-Petaling_Jaya_Petaling_District_Selangor.html",
        "https://www.tripadvisor.com.my/Restaurant_Review-g298570-d21163915-Reviews-Cafe_bistrot_David-Kuala_Lumpur_Wilayah_Persekutuan.html"
    ]

    def parse(self, response):

        restaurant_name = response.xpath("//*[@class='HjBfq']/text()").get()

        for d in response.xpath("//*[@class='review-container']"):

            id = d.attrib["data-reviewid"]

            date = d.xpath(".//*[@class='ratingDate']/@title").get()

            stay_date = d.xpath(
                ".//*[@class='prw_rup prw_reviews_stay_date_hsx']/text()").get()

            user = d.xpath(
                ".//*[@class='info_text pointer_cursor']/div/text()").get()

            badge = d.xpath(".//*[@class='badgeText']/text()").get()

            bubble_class = "ui_bubble_rating bubble"
            rating1 = d.xpath(f".//span[@class='{bubble_class}_10']").get()
            rating2 = d.xpath(f".//span[@class='{bubble_class}_20']").get()
            rating3 = d.xpath(f".//span[@class='{bubble_class}_30']").get()
            rating4 = d.xpath(f".//span[@class='{bubble_class}_40']").get()
            rating5 = d.xpath(f".//span[@class='{bubble_class}_50']").get()

            ratings = max([
                1 if rating1 is not None else 0,
                2 if rating2 is not None else 0,
                3 if rating3 is not None else 0,
                4 if rating4 is not None else 0,
                5 if rating5 is not None else 0
            ])

            title = d.xpath(".//span[@class='noQuotes']/text()").get()
            review_text = d.xpath(".//p[@class='partial_entry']/text()").get()

            yield {
                "restaurant": restaurant_name,
                "review_id": id,
                "date": datetime.strptime(date, "%d %B %Y"),
                "stay_date": stay_date.strip(),
                "user": user,
                "badge": badge,
                "rating": ratings,
                "title": title,
                "review": review_text
            }

        next_page = response.xpath(
            ".//*[@class='nav next ui_button primary']/@href").get()

        if next_page:

            sec = randint(1, 5)  # randomise pausing of seconds
            print(f"\npausing crawler for {sec} seconds...")
            time.sleep(sec)

            yield response.follow(
                response.urljoin(next_page),
                callback=self.parse
            )


if __name__ == "__main__":

    settings = {
        "FEEDS": {
            "reviews.csv": {
                "format": "csv",
                "overwrite": True
            }
        },
        # to avoid getting block, header the request with a user agent that looks authentic
        "USER_AGENT": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        # "USER_AGENT": "Googlebot/2.1 (+http://www.google.com/bot.html)"
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ReviewSpider)
    process.start()
