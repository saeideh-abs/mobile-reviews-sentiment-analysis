# -*- coding: utf-8 -*-
from __future__ import absolute_import
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from isna.items import IsnaItem

class IsnaSpiderSpider(CrawlSpider):
    name = 'isna_spider'
    start_urls = ['https://www.mobile.ir/phones/brands.aspx']
    rules = [
                Rule(LinkExtractor(allow=r'/phones/comments-\d+-[^/]+$',), callback='parse_comments', follow=False),
                Rule(LinkExtractor(allow=r'/phones/brands.aspx',), follow=True),
                Rule(LinkExtractor(allow=r'/brands/\d+-[^/]+$',), follow=True),
                Rule(LinkExtractor(allow=r'/phones/specifications-\d+-[^/]+$',), follow=True),
            ]

    def parse_comments(self, response):
        self.logger.info(f"\n ******************************************************************************\n")
        #print(response.request.url)
        item = IsnaItem()
        
        for comment in response.css('div.comment'):
            date = (''.join(comment.css('div.comment>h3>span>b::text').extract()).strip()).split('/')
            
            if (int(date[0]) >= 1397 and int(date[1]) >= 4):
                brand_model = ''.join(response.css('h2.pagetitle::text').extract()).strip()
                item['brand_model'] = brand_model[31:]
                item['holder'] = ''.join(comment.css('div.comment>h3>strong>a::text').extract()).strip() 
                item['date'] = ''.join(comment.css('div.comment>h3>span>b::text').extract()).strip()
                item['comment'] = ''.join(comment.css('div.comment>div.padd::text').extract()).strip()
                yield item
            
        pass
