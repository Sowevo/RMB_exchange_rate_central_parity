# RMB_exchange_rate_central_parity

## 人民币汇率中间价

查询 [人民币汇率中间价公告]( http://www.pbc.gov.cn/zhengcehuobisi/125207/125217/125925/index.html )并发送到钉钉

## 参数
 - num_pages 抓取多少页的公告,默认为10
 - time_interval 两次抓取间隔的秒数,默认为0.5
 - single 是否只抓取最新的一条,1为true,此时忽略--num_pages参数
 - access_token 发送钉钉消息的参数,access_token,不填不发钉钉消息
 - secret发送钉钉消息的参数,secret,不填不发钉钉消息

## 本机使用
  
  - 安装python依赖 `pip install -r requirements.txt`
  - 安装nodeJs 用来解析JS
  - 启动 
    ```shell
    $ python crawl.py --access_token=5fc5d5cfa6550becb02f034d4fbd671195b6cf01ffac95dc84d48ed1e290a63c --secret=SEC82c0cc25ccdff88c9c559b505fc08540e9a145991d4c76a177bb09480842ba5e
    ```
## docker 使用
  
  - 拉取镜像`docker pull sowevo/rmb_exchange_rate_central_parity:latest`
  - 启动容器
    ```shell
    $ docker run --rm rmb_exchange_rate_central_parity --access_token=5fc5d5cfa6550becb02f034d4fbd671195b6cf01ffac95dc84d48ed1e290a63c --secret=SEC82c0cc25ccdff88c9c559b505fc08540e9a145991d4c76a177bb09480842ba5e
    ```

