# AioPTTCrawler (PTT 網路版爬蟲)

This is Python Package use to crawl PTT's article data by using asyncio.

## Documentation

### [PyPi Page][]

[PyPi Page]:<https://pypi.org/project/AioPTTCrawler/>

```bash
pip install AioPTTCrawler
```

```python
from AioPTTCrawler import AioPTTCrawler
ptt_crawler = AioPTTCrawler()
```

## Usage

### get data from PTT

```python
ptt_crawler = AioPTTCrawler()

BOARD = "Gossiping"
ptt_data = ptt_crawler.get_board_latest_articles(board=BOARD, page_count=10)
```

```python
ptt_crawler = AioPTTCrawler()

BOARD = "Gossiping"
ptt_data = ptt_crawler.get_board_articles(board=BOARD, start_index=100, end_index=200)
```

#### ptt_data is a PTTData object. To extract data you need to use get_article_dict(), get_article_dataframe(), etc

---

### get dict from PTTData

```python
article_dict = ptt_data.get_article_dict()
comment_dict = ptt_data.get_comment_dict()
```

article's dict format

```json
[
    {
        "article" : "Article's ID. ex:M.1663144920.A.A6E",
        "article_title" : "Article's title. ex:[公告] 批踢踢27週年活動宣導公告更新",
        "user_id" : "Author's ID. ex: ubcs",
        "user_name" : "Author's name. ex:(覺★青年超冒險蓋)",
        "board" : "BBS Board ex: Gossiping",
        "datetime" : "Post time. ex: Wed Sep 14 16:41:58 2022.",
        "context" : "Context of article. ex: PTT 27 周年活動開始囉，本篇為置底宣導，詳情參閱下面資料...",
        "ip_address" : "IP address. ex: 59.120.192.119",
        "comment_list" : [
            {"comment_dict"},
            {"comment_dict"},
        ]
    }, {"..."}
]
```

comment's dict format

```json
[
    {
        "article_id" : "Article's ID. ex:M.1663144920.A.A6E",
        "tag" : "comment's reaction. ex: 推 噓 →",
        "user_id" : "User's ID. ex: bill403777",
        "comment_order" : "order of comment. ex: 1",
        "context" : "Context of comment. ex: 錢",
        "datetime" : "Post time. ex: 09/14 16:42",
        "ip_address" : "27.53.96.42",
    }, {"..."}
]
```

#### use this [article][] for example

[article]: https://www.ptt.cc/bbs/Gossiping/M.1663144920.A.A6E.html

## Comparsion

### Used time difference between normal method and async method

![time diff](/time-diff.png)

#### (unit: second)

## Support

You may report bugs, ask for help and discuss various other issues on the [issuse][]

[issuse]: https://github.com/DOUIF/aio-ptt-crawler/issues
