# coding=utf-8
import sys
import datetime

sys.path.append('../../')
from lxml import etree
import random
from pillow_crawler.main.crawler_manager import *
from pillow_crawler.crawler.base_crawler import *


class MeijingCrawler(BaseCrawler):
    def __init__(self):
        BaseCrawler.__init__(self, "Meijing")
        self.base_url = "https://sh.lianjia.com"
        self.total_page = 0
        self.cur_page = 0
        self.crawler_rules = [
            CrawlerRule(
                url_pattern=r"http://economy.nbd.com.cn/columns/590*",
                process_func=self.process_meijing_item,
            )
        ]

    def process_meijing_item(self, url, response):
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
    a_list = selector.xpath("//li[@class='u-news-title']/a")
    for div in a_list:
        # 显示名称
        title = div.get('title')
        title_url = div.get('href')
        storage.upsert_one({"title": title}, {
            "$set": {"title_url": title_url,
                     "update_time": datetime.datetime.now()}})
        # 翻页信息
        result = None
        try:
            result = selector.xpath("/html/body/div[4]/div[2]/div[2]/div[7]/div/span[@class='next']/a")[0]
        except IndexError as e:
            pass
        if result is not None:
            time.sleep(random.randint(3, 5))  # 随机睡3~5秒防止被封IP
            self.scheduler.put_url(result.get('href'))


def main():
    # 创建爬虫管理器，加载配置文件
    config_filepath = "conf.yaml"
    crawler_manager = CrawlerManager(config_filepath)
    # 创建爬虫，添加初始任务
    crawlers = [MeijingCrawler() for i in range(6)]
    crawler_manager.set_crawlers(crawlers)
    crawler_manager.add_task("http://economy.nbd.com.cn/columns/590")
    # 开启爬取
    crawler_manager.start()
    crawler_manager.join()


if __name__ == '__main__':
    main()
