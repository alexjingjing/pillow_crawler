# coding=utf-8
import sys
import datetime

sys.path.append('../../')
from lxml import etree
import random
from pillow_crawler.main.crawler_manager import *
from pillow_crawler.crawler.base_crawler import *


class LianjiaCrawler(BaseCrawler):
    def __init__(self):
        BaseCrawler.__init__(self, "Lianjia")
        self.base_url = "https://sh.lianjia.com"
        self.total_page = 0
        self.cur_page = 0
        self.crawler_rules = [
            CrawlerRule(
                url_pattern=r"https://sh.lianjia.com/ershoufang/rs*",
                process_func=self.process_lianjia_item,
            ),
            CrawlerRule(
                url_pattern=r"https://sh.lianjia.com/ershoufang/pg*",
                process_func=self.process_lianjia_item,
            )
        ]

    def process_lianjia_item(self, url, response):
        # 获取存储器
        storage = self.data_storage_manager.get_data_storage("mongodb_test")
        # 解析页面
        selector = etree.HTML(response)
        try:
            parse(self, storage, selector)
        except Exception as e:
            print(e)


def parse(self, storage, selector):
    # 获取页面信息
    result = selector.xpath("/html/body/div[4]/div[1]/ul/li")
    for div in result:
        # 显示名称
        house_name = div.xpath("div[1]/div[1]/a")[0].text
        house_des = div.xpath("div[1]/div[2]/div/text()")[0]
        house_type = div.xpath("div[1]/div[3]/div/text()")[0]
        house_location = div.xpath("div[1]/div[3]/div/a")[0].text
        house_follow = div.xpath("div[1]/div[4]/text()")[0]
        house_price = div.xpath("div[1]/div[6]/div[1]/span")[0].text
        house_price_unit = div.xpath("div[1]/div[6]/div[1]/text()")[0]
        house_per_price = div.xpath("div[1]/div[6]/div[2]")[0].get("data-price")
        house_attr_spans = div.xpath("div[1]/div[5]/span")
        house_detail_href = div.xpath("a")[0].get("href")
        house_subway = ''
        house_five = ''
        house_taxfree = ''
        house_haskey = ''
        for span in house_attr_spans:
            if span.get("class") == 'subway':
                house_subway = span.text
            elif span.get("class") == 'five':
                house_five = span.text
            elif span.get("class") == 'taxfree':
                house_taxfree = span.text
            if span.get("class") == 'haskey':
                house_haskey = span.text
        storage.upsert_one({"house_name": house_name}, {
            "$set": {"house_des": house_des, "house_type": house_type, "house_location": house_location,
                     "house_follow": house_follow, "house_price": float(house_price),
                     "house_price_unit": house_price_unit,
                     "house_per_price": float(house_per_price), "house_subway": house_subway, "house_five": house_five,
                     "house_taxfree": house_taxfree, "house_haskey": house_haskey,
                     "house_detail_href": house_detail_href,
                     "update_time": datetime.datetime.now()}})
        # 翻页信息
        try:
            result = selector.xpath("/html/body/div[4]/div[1]/div[7]/div[2]/div")[0]
        except IndexError as e:
            pass
        if result is not None:
            self.total_page = eval(result.get('page-data'))['totalPage']
            self.cur_page += 1
            if not self.cur_page > self.total_page:
                time.sleep(random.randint(3, 5))  # 随机睡3~5秒防止被封IP
                self.scheduler.put_url(self.base_url + str(result.get('page-url')).format(page=self.cur_page))


def main():
    # 创建爬虫管理器，加载配置文件
    config_filepath = "conf.yaml"
    crawler_manager = CrawlerManager(config_filepath)
    # 创建爬虫，添加初始任务
    crawlers = [LianjiaCrawler() for i in range(6)]
    crawler_manager.set_crawlers(crawlers)
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs闵行/")
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs三林/")
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs浦江/")
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs后滩/")
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs前滩/")
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs张江/")
    # 开启爬取
    crawler_manager.start()
    crawler_manager.join()


if __name__ == '__main__':
    main()
