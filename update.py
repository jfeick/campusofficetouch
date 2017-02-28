from scrapy import signals
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from uni_weimar.spiders.eventcal import CalendarSpider
from uni_weimar.spiders.journal import JournalSpider
from uni_weimar.spiders.piazza import PiazzaSpider
from uni_weimar.spiders.showcase import ShowcaseSpider

import json
from time import strptime
from datetime import datetime, date
import locale

from scrapy.exporters import JsonItemExporter

class UniCrawler:
    def __init__(self):
        self.calendar_items = []
        self.journal_items = []
        self.piazza_items = []
        self.showcase_items = []

    def calendar_item_passed(self, item):
        self.calendar_items.append(item)

    def journal_item_passed(self, item):
        self.journal_items.append(item)

    def piazza_item_passed(self, item):
        self.piazza_items.append(item)

    def showcase_item_passed(self, item):
        self.showcase_items.append(item)

    def crawl(self):
        configure_logging({'LOG_FILE':'scrapy.log', 'LOG_LEVEL':'WARNING'})
        runner = CrawlerRunner()
        calendar_crawler = runner.create_crawler(CalendarSpider)
        calendar_crawler.signals.connect(self.calendar_item_passed, signal=signals.item_scraped)
        journal_crawler = runner.create_crawler(JournalSpider)
        journal_crawler.signals.connect(self.journal_item_passed, signal=signals.item_scraped)
        piazza_crawler = runner.create_crawler(PiazzaSpider)
        piazza_crawler.signals.connect(self.piazza_item_passed, signal=signals.item_scraped)
        showcase_crawler = runner.create_crawler(ShowcaseSpider)
        showcase_crawler.signals.connect(self.showcase_item_passed, signal=signals.item_scraped)

        runner.crawl(calendar_crawler)
        runner.crawl(journal_crawler)
        runner.crawl(piazza_crawler)
        runner.crawl(showcase_crawler)

        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()

    def sort_calendar_items(self):
        locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))
        self.calendar_items.sort(key=lambda x: (strptime(x['month'], '%b').tm_mon, int(x['day_of_month'])))
        current_year = date.today().year
        for item in self.calendar_items:
            if len(item['day_of_month']) == 1:
                item['day_of_month'] = '0' + item['day_of_month']
            item_date = datetime.strptime(item['day_of_month'] + ' ' + item['month'] + ' '
                            + str(current_year), '%d %b %Y')
            if item_date.strftime('%a') != item['weekday']:
                item_date = datetime.strptime(item['day_of_month'] + ' ' + item['month'] + ' '
                                + str(current_year + 1), '%d %b %Y')
            #item['weekday'] = item_date.strftime('%a')
            item['long_weekday'] = item_date.strftime('%A')
            item['long_month'] = item_date.strftime('%B')
            item['year'] = item_date.strftime('%Y')

    def sort_piazza_items(self):
        locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
        self.piazza_items.sort(key=lambda x: datetime.strptime(x['date'], '%a, %d %b %Y %H:%M:%S %Z'))
        self.piazza_items.reverse()

        for item in self.piazza_items:
            locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
            dt = datetime.strptime(item['date'], '%a, %d %b %Y %H:%M:%S %Z')
            locale.setlocale(locale.LC_ALL, ('de_DE', 'UTF-8'))
            item['german_date'] = dt.strftime('%d. %B')
            item['time'] = dt.strftime('%H:%M')

    def index_items(self):
        for i, item in enumerate(self.calendar_items, start=1):
            item['id'] = i
        for i, item in enumerate(self.showcase_items, start=1):
            item['id'] = i
        for i, item in enumerate(self.journal_items, start=1):
            item['id'] = i
        for i, item in enumerate(self.piazza_items, start=1):
            item['id'] = i

    def dump_items(self):
        with open('calendar.json', 'wb') as outfile:
            exporter = JsonItemExporter(outfile)
            exporter.start_exporting()
            for item in self.calendar_items:
                exporter.export_item(item)
            exporter.finish_exporting()
        with open('piazza.json', 'wb') as outfile:
            exporter = JsonItemExporter(outfile)
            exporter.start_exporting()
            for item in self.piazza_items:
                exporter.export_item(item)
            exporter.finish_exporting()
        with open('journal.json', 'wb') as outfile:
            exporter = JsonItemExporter(outfile)
            exporter.start_exporting()
            for item in self.journal_items:
                exporter.export_item(item)
            exporter.finish_exporting()
        with open('showcase.json', 'wb') as outfile:
            exporter = JsonItemExporter(outfile)
            exporter.start_exporting()
            for item in self.showcase_items:
                print("showcase item")
                exporter.export_item(item)
            exporter.finish_exporting()


#@defer.inlineCallbacks
#def crawl():
#    yield runner.crawl(calendar_crawler)
#    #dispatcher.connect(journal_item_passed, signals.item_scraped)
#    #yield runner.crawl(JournalSpider)
#    reactor.stop()
#
#crawl()
#reactor.run()
def main():
    unicrawler = UniCrawler()
    unicrawler.crawl()
    unicrawler.sort_calendar_items()
    unicrawler.sort_piazza_items()
    unicrawler.index_items()
    unicrawler.dump_items()

if __name__ == "__main__":
    main()
