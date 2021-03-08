import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import NbsrsItem
from itemloaders.processors import TakeFirst


class NbsrsSpider(scrapy.Spider):
	name = 'nbsrs'
	start_urls = ['https://www.nbs.rs/sr_RS/drugi-nivo-navigacije/pres/arhiva-vesti/index.html']

	def parse(self, response):
		post_links = response.xpath('//table[@id="news"]//form/@action').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="pagination"]/li/a[text()="»"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//div[@class="number_list pj"]/h3/text()').get()
		description = response.xpath('//div[@class="number_list pj"]//text()[normalize-space() and not(ancestor::h3 | ancestor::i | ancestor::video)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//i/text()').get()

		item = ItemLoader(item=NbsrsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
