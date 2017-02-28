import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from io import BytesIO
from PIL import Image, ImageOps
import os

import logging
import json

#from uni_weimar.items import JournalItem

import re
import lxml
import logging


def clean(dirty_string):
    res = dirty_string.replace('\t', '')
    res = res.replace('\n', '')
    res = res.replace('\r', '')
    return res.strip()

class CalendarItem(scrapy.Item):
    title = scrapy.Field()
    weekday = scrapy.Field()
    day_of_month = scrapy.Field()
    month = scrapy.Field()
    subtitle = scrapy.Field()
    maininfo = scrapy.Field()
    bodytext = scrapy.Field()
    day_of_week = scrapy.Field()
    year = scrapy.Field()
    long_month = scrapy.Field()
    long_weekday = scrapy.Field()
    id = scrapy.Field()

class CalendarSpider(scrapy.Spider):
    name = "eventcal"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/aktuell/veranstaltungskalender/"   ]

    def parse(self, response):

        list_items = response.css('.record01')
        for list_item in list_items:
            date = list_item.css('.my_datesheet')
            weekday = date.css('.weekday').xpath('a/text()').extract()[0]
            day_of_month = date.css('.day_of_month').xpath('a/text()').extract()[0]
            month = date.css('.month').xpath('a/text()').extract()[0]
            text = list_item.css('.text01')
            title = text.css('h2').xpath('a/text()').extract()[0]
            href = text.css('h2').xpath('a/@href')

            subtitle = text.css('.cal_subtitle').xpath('text()').extract()
            subtitle = "".join(subtitle)

            maininfo = text.css('.cal_maininfo').xpath('*').extract()
            maininfo = "".join(maininfo)

            url = response.urljoin(href.extract()[0])

            item = CalendarItem()
            item['weekday'] = clean(weekday)
            item['day_of_month'] = clean(day_of_month)
            item['month'] = clean(month)
            item['subtitle'] = clean(subtitle)
            item['title'] = clean(title)
            item['maininfo'] = clean(maininfo);

            self.logger.info("Yielding item")

            yield scrapy.Request(url, callback=self.parse_calendar_item, meta={'item': item})
            #yield item

    def parse_calendar_item(self, response):
        item = response.meta['item']
        bodytext = response.css('.cal_bodytext').xpath('*').extract()
        bodytext = "".join(bodytext)

        # strip links with regex
        p = re.compile(r"<\/?a(?:(?= )[^>]*)?>")
        bodytext = re.sub(p, "", bodytext)

        item['bodytext'] = bodytext

        yield item
