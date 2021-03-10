import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AndelskassenItem
from itemloaders.processors import TakeFirst


pattern = r'(\xa0)?'

class AndelskassenSpider(scrapy.Spider):
	name = 'andelskassen'
	start_urls = ['https://www.andelskassen.dk/om-os/nyheder/?page=1']
	urls_list =[]
	page = 1
	def parse(self, response):
		articles = response.xpath('//article[@class="article"]')
		for article in articles:
			date = article.xpath('.//div[@class="date-inner"]/span/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

			self.page +=1
			if self.page < int(response.xpath('//div[@class="pull-right"]/text()').get().split(' af ')[1].strip()):
				next_page = f'https://www.andelskassen.dk/om-os/nyheder/?page={self.page}'
				yield response.follow(next_page, self.parse)

	def parse_post(self, response,date):

		title = response.xpath('//div[@class="col-sm-8 col-xs-12 col-print-full"]//h1/text()').get()
		content = response.xpath('//section[@class="page-content"]//text()[not (ancestor::h1) and not (ancestor::p[@class="text-right"]) and not (ancestor::script)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=AndelskassenItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
