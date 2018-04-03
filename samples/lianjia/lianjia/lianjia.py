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
        mongodb = self.data_storage_manager.get_data_storage("mongodb_test")
        # 解析页面
        selector = etree.HTML(response)
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
            mongodb.upsert_one({"house_name": house_name}, {
                "$set": {"house_des": house_des, "house_type": house_type, "house_location": house_location,
                         "house_follow": house_follow, "house_price": house_price, "house_price_unit": house_price_unit,
                         "house_per_price": house_per_price, "update_time": datetime.datetime.now()}})
        # 翻页信息
        result = selector.xpath("/html/body/div[4]/div[1]/div[7]/div[2]/div")[0]
        if result is not None:
            self.total_page = eval(result.get('page-data'))['totalPage']
            self.cur_page += 1
            if not self.cur_page > self.total_page:
                time.sleep(random.randint(2, 4))  # 随机睡2~4秒防止被封IP
                self.scheduler.put_url(self.base_url + str(result.get('page-url')).format(page=self.cur_page))


def main():
    # 创建爬虫管理器，加载配置文件
    config_filepath = "conf.yaml"
    crawler_manager = CrawlerManager(config_filepath)
    # 创建爬虫，添加初始任务
    crawlers = [LianjiaCrawler() for i in range(3)]
    crawler_manager.set_crawlers(crawlers)
    crawler_manager.add_task("https://sh.lianjia.com/ershoufang/rs%E9%97%B5%E8%A1%8C/")
    # 开启爬取
    crawler_manager.start()
    crawler_manager.join()


if __name__ == '__main__':
    main()
