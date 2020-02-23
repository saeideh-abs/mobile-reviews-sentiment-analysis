# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IsnaItem(scrapy.Item):
    # define the fields for your item here like:
    brand_model = scrapy.Field()
    holder = scrapy.Field()
    date = scrapy.Field()
    comment = scrapy.Field()
    pass
