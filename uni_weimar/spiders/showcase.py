import scrapy
import logging
import re
import json


from uni_weimar.items import ShowCaseItem, ShowCaseImage, ShowCaseVideo

class ShowcaseSpider(scrapy.Spider):
    name = "showcase"
    allowed_domains = ["uni-weimar.de"]
    start_urls = [
    "http://www.uni-weimar.de/de/universitaet/profil/experiment-bauhaus/"
    ]

    def parse(self, response):
        links = response.css(".project-link")
        # we are selecting links from a svg namespace. selectors extract xlink:href attribute
        for element in links:
            href = element.xpath("@*[name()='xlink:href']")
            self.logger.info('URL extracted: %s', href.extract()[0])
            url = response.urljoin(href.extract()[0])
            script = """
            function main(splash)
            local url = splash.args.url
            assert(splash:autoload("https://m18.uni-weimar.de/touchscreen/divclip.js"))
            assert(splash:go(url))
            assert(splash:wait(0.5))
            local divclip = splash:evaljs('divclip.bySel(".information")')
            return { divclip = divclip, html = splash:html() }
            end
            """

            yield scrapy.Request(url, callback=self.parse_showcase_item, meta={
            'splash': {
                'args': { 'lua_source': script },
                'endpoint': 'execute',
            }
            })

    def parse_showcase_item(self, response):

        data = json.loads(response.body_as_unicode())
        body = scrapy.selector.Selector(text=data['html'])

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
        project_information = information_node.css('div.information-column.first').extract()[0]
        project_description = information_node.css('div.information-column.last').extract()[0]

        project_information = project_information.replace('\t', '')
        project_information = project_information.replace('\n', '')
        project_information = project_information.replace('\r', '')
        project_description = project_description.replace('\t', '')
        project_description = project_description.replace('\n', '')
        project_description = project_description.replace('\r', '')

        #item['information'] = project_information
        #item['description'] = project_description

        content_html = data['divclip']
        item['information'] = content_html

        vitrine_node = body.css('article.vitrine')
        figures = vitrine_node.css('#tx-buw-showcase-images > div.csc-gallery-slideshow-images > figure')
        image_items = []
        for figure in figures:
            img = figure.css('img')
            img_src = "http://www.uni-weimar.de" + img.xpath('@src').extract()[0]
            self.logger.info("URL??? -> %s", img_src)
            img_height = img.xpath('@height').extract()[0]
            img_width = img.xpath('@width').extract()[0]

            image_item = ShowCaseImage()
            image_item['src'] = img_src
            image_item['width'] = img_width
            image_item['height'] = img_height
            image_items.append(image_item)

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
