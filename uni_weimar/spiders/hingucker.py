import scrapy
import logging
import re

from uni_weimar.items import HinguckerItem, HinguckerImage

class HinguckerSpider(scrapy.Spider):
    name = "hingucker"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/aktuell/bauhausjournal-online/hingucker/",
    "http://www.uni-weimar.de/de/universitaet/aktuell/bauhausjournal-online/hingucker/seite/1/",
    "http://www.uni-weimar.de/de/universitaet/aktuell/bauhausjournal-online/hingucker/seite/2/"
    ]

    def parse(self, response):
        records = response.css(".record01.item-.type-news")
        for record in records:
            link = record.css("div.thumb > span > div.thumb > span > a")
            link_href = link.xpath("@href").extract()[0]
            thumbnail_src = link.xpath("img/@src").extract()[0]
            item = HinguckerItem()
            item["thumbnail_src"] = response.urljoin(thumbnail_src)
            url = response.urljoin(link_href)
            yield scrapy.Request(url, callback=self.parse_hingucker_item, meta={'item': item})

    def parse_hingucker_item(self, response):
        item = response.meta['item']
        title = response.css(".news_title.csc-firstHeader").xpath("text()").extract()[0]
        item['title'] = title
        image = response.css(".csc-textpic-imagewrap") #.xpath("figure/a/img")
        figures = response.css(".csc-textpic-image")
        image_items = []
        for figure in figures:
            image = figure.xpath("a/img")
            image_item = HinguckerImage()
            if len(image):
                image_item['caption'] = image.xpath("@alt").extract()[0]
                image_item['src'] = response.urljoin(image.xpath("@src").extract()[0])
                image_item['width'] = image.xpath("@width").extract()[0]
                image_item['height'] = image.xpath("@height").extract()[0]

            else:
                image = figure.xpath("img")
                image_item['caption'] = figure.xpath("figcaption/text()").extract()[0]
                image_item['src'] = response.urljoin(image.xpath("@src").extract()[0])
                image_item['width'] = image.xpath("@width").extract()[0]
                image_item['height'] = image.xpath("@height").extract()[0]
                image_items.append(image_item) 
        item['images'] = image_items
        yield item

