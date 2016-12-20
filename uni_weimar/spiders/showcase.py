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


class ShowCaseItem(scrapy.Item):
    title = scrapy.Field()
    information = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    video = scrapy.Field()
    image_urls = scrapy.Field()
    author = scrapy.Field()
    
class ShowCaseImage(scrapy.Item):
    src = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    #image_urls = scrapy.Field()

class ShowCaseVideo(scrapy.Item):
    src = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()

class ShowcaseImagesPipeline(ImagesPipeline):
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

class ShowcaseSpider(scrapy.Spider):
    name = "showcase"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/profil/experiment-bauhaus/"
    ]
    # DEBUG!
    count = 0
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'scrapy.pipelines.images.ImagesPipeline': 100,
            'uni_weimar.spiders.showcase.ShowcaseImagesPipeline': 100,
        },
        'IMAGES_STORE': 'showcase',
        'IMAGES_THUMBS': {
            'small': (130, 130),
            'big': (434, 468),
        },
    }

    def parse(self, response):
        links = response.css(".project-link")
        # we are selecting links from a svg namespace. selectors extract xlink:href attribute
        for element in links:
            href = element.xpath("@*[name()='xlink:href']")
            self.logger.info('URL extracted: %s', href.extract()[0])
            url = response.urljoin(href.extract()[0])
          
            yield scrapy.Request(url, callback=self.parse_showcase_item)

    def parse_showcase_item(self, response):

        #data = json.loads(response.body_as_unicode())
        #body = scrapy.selector.Selector(text=data['html'])

        body = response
        title_node = body.css('.projecttitle')
        title = title_node.xpath('./h2/text()').extract()

        item = ShowCaseItem()

        if len(title):
            title = title[0]
            self.logger.info("Title: %s", title)
            item['title'] = title
        else:
            return

        information_node = body.css('article.information')
        project_information = information_node.css('div.information-column.first .bgbox').xpath('*').extract()
        project_information = "".join(project_information)
        author = information_node.css('div.information-column.first .bgbox p:first-of-type').xpath('text()').extract()[0]
        project_description = information_node.css('div.information-column.last .bgbox').xpath('*').extract()
        project_description = "".join(project_description)

        project_information = project_information.replace('\t', '')
        project_information = project_information.replace('\n', '')
        project_information = project_information.replace('\r', '')
        project_description = project_description.replace('\t', '')
        project_description = project_description.replace('\n', '')
        project_description = project_description.replace('\r', '')
        author = author.replace('\t', '')
        author = author.replace('\n', '')
        author = author.replace('\r', '')

        #item['information'] = project_information
        #item['description'] = project_description

        #content_html = data['divclip']

        # strip links from content html
        p = re.compile(r"<\/?a(?:(?= )[^>]*)?>")
        project_information = re.sub(p, "", project_information)
        project_description = re.sub(p, "", project_description)

        item['information'] = project_information
        item['author'] = author
        item['description'] = project_description

        vitrine_node = body.css('article.vitrine')
        figures = vitrine_node.css('#tx-buw-showcase-images > div.csc-gallery-slideshow-images > figure')
        image_items = []
        item['image_urls'] = []
        for figure in figures:
            # import ipdb; ipdb.set_trace()
            img = figure.css('img')
            img_src = img.xpath('@src').extract()[0]
            self.logger.info("URL??? -> %s", img_src)
            img_height = img.xpath('@height').extract()[0]
            img_width = img.xpath('@width').extract()[0]

            image_item = ShowCaseImage()
            image_item['src'] = img_src
            image_item['width'] = img_width
            image_item['height'] = img_height
            #image_item['image_urls'] = [img_src]
            image_items.append(image_item)
            item['image_urls'].append(img_src)

        item['images'] = image_items

        video_node = vitrine_node.css('#ty-buw-showcase-video')
        if len(video_node):
            iframe = video_node.css('iframe')
            video_src = iframe.xpath('@src').extract()[0]
            video_width = iframe.xpath('@width').extract()[0]
            video_height = iframe.xpath('@height').extract()[0]

            video_item = ShowCaseVideo()
            video_item['src'] = video_src
            video_item['width'] = video_width
            video_item['height'] = video_height

            item['video'] = dict(video_item)


        yield item
