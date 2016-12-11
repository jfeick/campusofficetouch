import scrapy
import logging
import re

from uni_weimar.items import ShowCaseItem, ShowCaseImage, ShowCaseVideo

class ShowcaseSpider(scrapy.Spider):
    name = "showcase"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/aktuell/veranstaltungskalender/"
    ]

    def parse(self, response):
        listview = response.css("div.listview.listview-content.listview-201.listview-content-201")
        # we are selecting links from a svg namespace. selectors extract xlink:href attribute
        records = listview.css("div.record01")
        for record in records:
            link = record.css("div.text01 > h2 > a")
            href = link.xpath("@href")
            url = response.urljoin(href.extract()[0])
            yield scrapy.Request(url, callback=self.parse_eventcal_item)

    def parse_eventcal_item(self, response):
        pass
