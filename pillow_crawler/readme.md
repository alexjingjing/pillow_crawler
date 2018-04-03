# pillow_crawler

[toc]

## 概述


## 安装

依赖软件
* python 3.6

依赖库
* yaml: ``` pip install PyYaml```
* mysqlclient: ```pip install mysqlclient```
* requests: ```pip install requests```，性能高
* lxml: ```pip install lxml```，性能高，可用xpath，实测版本4.1.1s
* pymongo: ```pip install pymongo``` 

## 配置
### mongodb
```conf
data_storage:
  - type: mongodb
    name: mongodb_test
    replicaset: shangchengrepl // 副本集名称，单击可不填
    ip: 192.168.2.65 // 必填，mongodb地址
    db: custom // 必填，数据库名称
    col: lianjia // 必填，数据集名称
```