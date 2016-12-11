# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ShowCaseItem(scrapy.Item):
    title = scrapy.Field()
    information = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    video = scrapy.Field()
    
class ShowCaseImage(scrapy.Item):
    src = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()

class ShowCaseVideo(scrapy.Item):
    src = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()


class JournalItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    image_src = scrapy.Field()
    image_width = scrapy.Field()
    image_height = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    teaser_text = scrapy.Field()
    article_body = scrapy.Field()

class HinguckerItem(scrapy.Item):
    title = scrapy.Field()
    thumbnail_src = scrapy.Field()
    images = scrapy.Field()

class HinguckerImage(scrapy.Item):
    src = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    caption = scrapy.Field()
