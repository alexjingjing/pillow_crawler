# coding=utf-8
import logging

from pymongo import MongoClient

from pillow_crawler.data_storage.data_storage import DataStorage
from pillow_crawler.system.dict_util import *


class MongoStorage(DataStorage):
    def __init__(self, config):
        connect = False if not check_key_return_bool(config, ["connect"]) else config['connect']
        self.sys_log = logging.getLogger("sys")
        self.sys_log.debug("..MongoClient init begin")
        replica_flag = check_key_return_bool(config, ["replicaset"])
        if not replica_flag:
            self.sys_log.debug("..no replica config found, start as standalone")
        else:
            self.sys_log.debug("..replica config found")
        if not check_key_return_bool(config, ['ip', 'col', 'db']):
            raise Exception("MongoDB配置文件错误，请确认ip,collection,database填写正确")
        if replica_flag:
            self.client = MongoClient(config['ip'], replicaset=config['replicaset'], connect=connect)
        else:
            self.client = MongoClient(config['ip'], connect=connect)
        self.db = self.client[config['db']]
        self.col = self.db[config['col']]
        self.sys_log.debug("..MongoStorage init done")

    def insert_one(self, item):
        self.col.insert_one(item)

    def upsert_one(self, query_filter, item):
        self.col.update_one(query_filter, item, upsert=True)
