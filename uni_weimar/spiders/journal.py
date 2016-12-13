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
    #image_full = scrapy.Field()
    #image_big = scrapy.Field()
    #image_small = scrapy.Field()

class JournalImagesPipeline(ImagesPipeline):
    def convert_image(self, image, size=None):
        if image.format != 'RGB':
            image = image.convert('RGB')
        if size:
            image = ImageOps.fit(image, size, Image.ANTIALIAS)
        buf = BytesIO()
        image.save(buf, 'PNG')
        return image, buf



    def item_completed(self, results, item, info):
        # import ipdb; ipdb.set_trace()
        #if len(results) and 'path' in results[0][1]:
        #    results[0][1]['path'] = os.path.basename(results[0][1]['path'])
        for result in results:
            result[1]['path'] = os.path.basename(result[1]['path'])
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        return item


class JournalSpider(scrapy.Spider):
    name = "journal"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/aktuell/bauhausjournal-online/"   ]

    custom_settings = {
        'ITEM_PIPELINES': {
            # 'scrapy.pipelines.images.ImagesPipeline': 100,
            'uni_weimar.spiders.journal.JournalImagesPipeline': 100,
        },
        'IMAGES_STORE': 'journal',
        'IMAGES_THUMBS': {
            'small': (130, 130),
            'big': (434, 468),
        },
    }
    def parse(self, response):

        self.logger.info("Journal parsing...")
        #list_items = response.css('#content_main .listarea .item')
        list_items = response.css('.listview-content .item')
        list_items += response.css('.listview-content .item-view-default')
        self.logger.info("Len of list_items: {}".format(len(list_items)))
        # get image
        for list_item in list_items:
            image = list_item.css('img')
            image_href = image.xpath('@src').extract()[0]
            image_width = image.xpath('@width').extract()[0]
            image_height = image.xpath('@height').extract()[0]
            image_url = response.urljoin(image_href)
            title = list_item.css('h2').xpath('a/text()').extract()[0]
            date = list_item.css('.datetime strong').xpath('text()').extract()[0]
            href = list_item.css('h2').xpath('a/@href')
            teaser_text = list_item.css('h3').xpath('text()').extract()[0]

            url = response.urljoin(href.extract()[0])

            item = JournalItem()
            item['title'] = title
            item['date'] = date
            item['image_src'] = image_url
            item['image_width'] = image_width
            item['image_height'] = image_height
            item['teaser_text'] = teaser_text

            self.logger.info("Yielding item")

            yield scrapy.Request(url, callback=self.parse_journal_item, meta={'item': item})


            # script = """
            # function main(splash)
            # local url = splash.args.url
            # assert(splash:autoload("https://m18.uni-weimar.de/touchscreen/divclip.js"))
            # assert(splash:go(url))
            # assert(splash:wait(0.5))
            # local divclip = splash:evaljs('divclip.bySel(".content_main")')
            # return { divclip = divclip }
            # end
            # """

            # yield scrapy.Request(url, callback=self.parse_showcase_item, \
            # meta={
            #     'item': item,

            #     'splash': {
            #   'args': {'lua_source': script},
            #   'endpoint': 'execute',
            #     }
            # })

    def parse_journal_item(self, response):
        item = response.meta['item']

        # extract image
        image = response.css('.csc-textpic img')
        image_href = image.xpath('@src').extract()[0]
        item['image_urls'] = [response.urljoin(image_href)]

        #content_html = response.css('.content_main').extract()[0]
        paragraphs = response.css('.news-text-wrap').xpath('*').extract()
        article_body = ""
        for paragraph in paragraphs:
            article_body += paragraph
        #data = json.loads(response.body_as_unicode())
        #content_html = data['divclip']

        # make our links absolute
        #content_html = lxml.html.make_links_absolute(content_html, "http://www.uni-weimar.de")

        # strip links with regex
        p = re.compile(r"<\/?a(?:(?= )[^>]*)?>")
        article_body = re.sub(p, "", article_body)

        item['article_body'] = article_body

        yield item
