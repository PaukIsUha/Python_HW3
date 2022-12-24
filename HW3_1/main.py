import scrapy

class SteamSpider(scrapy.Spider):
    __link__ = 'https://store.steampowered.com/search/?sort_by=&sort_order=0&term=souls%20like&supportedlang=russian&page='

    def parse(self, response):
        for i in response.xpath('//a[@data-gpnav="item"]/@href'):
            yield response.follow(i, callback=self.parse_page)
        yield response.follow(SteamSpider.__link__ + '2', callback=self.parse)

    @staticmethod
    def parse_page(response):
        path_for_parse = []
        for i in response.xpath('//div[@class="blockbg"]/a/text()'):
            path_for_parse.append(i.get())
        path_for_parse = path_for_parse[1:]
        resp = response.xpath('//div[@class="date"]/text()').get()
        if resp and int(resp.split()[2]) <= 2000:
            return
        yield {
            'title': response.xpath('//div[@id="appHubAppName_responsive"]/text()').get(), 'path': '/'.join(path_for_parse),
            'reviews': ' '.join([x.get() for x in response.xpath('//div[@class="summary_section"]/span/text()')]),
            'release date': resp, 'developer': response.xpath('//div[@id="developers_list"]/a/text()').get(),
            'popular tags': ', '.join([x.get().strip() for x in response.xpath('//div[@class="glance_tags popular_tags"]/a/text()')]),
            'price': response.xpath('//div[@class="discount_final_price"]/text() | //div[@class="game_purchase_price price"]/text()').get().strip(),
            'platforms available': ', '.join([x.get().strip() for x in response.xpath('//div[@class="sysreq_contents"]/div/@data-os')])
        }
