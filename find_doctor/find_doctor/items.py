# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Person(scrapy.Item):
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    role = scrapy.Field()
    title = scrapy.Field()
    workplace = scrapy.Field()
    doc_updated = scrapy.Field()
    download_date = scrapy.Field()
    url = scrapy.Field()
    email = scrapy.Field()