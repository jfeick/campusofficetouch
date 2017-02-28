import scrapy
import logging
import re
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from io import BytesIO
from PIL import Image, ImageOps
import os

#from uni_weimar.items import ShowCaseItem, ShowCaseImage, ShowCaseVideo


class PiazzaItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    author = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
    german_date = scrapy.Field()
    time = scrapy.Field()
    id = scrapy.Field()


class PiazzaImagesPipeline(ImagesPipeline):
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

class PiazzaSpider(scrapy.Spider):
    name = "piazza"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/aktuell/pinnwaende/rss/bereich/piazza/"
    ]
    # DEBUG!
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'scrapy.pipelines.images.ImagesPipeline': 100,
            'uni_weimar.spiders.piazza.PiazzaImagesPipeline': 100,
        },
        'IMAGES_STORE': 'piazza',
        'IMAGES_THUMBS': {
            'small': (130, 130),
            'big': (434, 468),
        },
    }

    def parse(self, response):

        items = response.xpath('//item')
        self.logger.info("Lenght of items: {}".format(len(items)))
        for item in items:
            description = item.xpath('description/text()').extract()
            description = "".join(description)
            description = description.replace('\n','</br>')
            title = item.xpath('title/text()').extract()
            title = "".join(title)
            author = item.xpath('author/text()').extract()
            author = "".join(author)
            date = item.xpath('pubDate/text()').extract()
            date = "".join(date)
            image_urls = item.xpath('enclosure/@url').extract()
            if '' in image_urls:
                image_urls.remove('')
            broken_url = "https://www.uni-weimar.de/"
            if broken_url in image_urls:
                image_urls.remove(broken_url)

            piazza_item = PiazzaItem()
            piazza_item['title'] = title
            piazza_item['description'] = description
            piazza_item['author'] = author
            piazza_item['date'] = date
            piazza_item['image_urls'] = image_urls

            yield piazza_item

        # we are selecting links from a svg namespace. selectors extract xlink:href attribute
        # for element in links:
        #     href = elementkku.xpath("@*[name()='xlink:href']")
        #     self.logger.info('URL extracted: %s', href.extract()[0])
        #     url = response.urljoin(href.extract()[0])

        #     yield scrapy.Request(url, callback=self.parse_showcase_item)
