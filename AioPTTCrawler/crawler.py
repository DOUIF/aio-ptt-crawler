import asyncio
import re
from datetime import datetime, timedelta

import aiohttp
from lxml import etree

from .model import Article, Comment
from .ptt_data import PTTData


class Crawler:
    PTT_URL: str = "https://www.ptt.cc"
    COOKIES: dict[str:str] = {"over18": "1"}
    article_filed: list[str] = [""]

    # initial Crawler
    def __init__(self, board: str, page_number: int) -> None:
        self.board = board
        self.page_number = page_number

    # get ptt board articles with specific page
    async def get_specific_page_data(self) -> PTTData:
        """
        Getting PTT board's articles with specific page.

        Parameters:
        None

        Returns:
        PTTData: preprocessed data from website response
        """
        print(f"Start crawling {self.board}: {self.page_number}")
        url = f"{Crawler.PTT_URL}/bbs/{self.board}/index{self.page_number}.html"
        try:
            result = await self.get_url_data(url)
        except Exception as e:
            print(e)
            print(f"{self.board}: getting {url} error.")
            return None
        processed_result = await self.processing_data(result)
        print(f"Finish crawling {self.board}: {self.page_number}")
        return processed_result

    # get original data from url
    async def get_url_data(self, url: str) -> str:
        """
        Getting data from url with async HTTP request.

        Parameters:
        url (str): url where data comes from

        Returns:
        str: original response text
        """
        # create async http session
        async with aiohttp.ClientSession() as session:
            # get data from async http request
            async with session.get(url=url, cookies=Crawler.COOKIES) as response:
                # waiting for the data to be received
                html = await response.text(encoding="utf-8")
                # return original data
                return html

    # processing data
    async def processing_data(self, original_text: str) -> PTTData:
        # part 1. remove on-top articles
        tree = self.__remove_on_top_article(etree.HTML(original_text))

        # part 2. get article links
        article_links, article_ids = self.__get_article_links(tree)
        # article_links, article_ids = ["https://www.ptt.cc/bbs/Gossiping/M.1663144920.A.A6E.html"], ["M.1663144920.A.A6E"]

        # part 3. get article content
        article_content = await self.__get_article_content(article_links)

        # part 4. filter article content
        ptt_data = self.__filter_article_content(article_content, article_ids)

        return ptt_data

    # part 1. remove on-top article in etree
    def __remove_on_top_article(self, tree: etree.HTML) -> etree.HTML:
        """
        Removing on-top article by detect on-top article separate line in article html div.

        Parameters:
        tree (etree.HTML)

        Returns:
        etree.HTML
        """
        on_top_article_sep = False
        article_separate_line_xpath = "r-list-sep"
        article_xpath = '//*[@id="main-container"]/div[2]/div'
        # loop all article node and remove on-top articles
        for node in tree.xpath(article_xpath):
            # get html div class name
            class_name = node.get("class")

            # "r-list-sep" means the separate line between normal articles and on-top articles
            if class_name == article_separate_line_xpath:
                on_top_article_sep = True

            # remove node if meet the separate line
            if on_top_article_sep:
                node.getparent().remove(node)

        # return processed etree
        return tree

    # part 2. get links from etree
    def __get_article_links(self, tree: etree.HTML) -> list[str]:
        """
        Get article links from etree by xpath

        Parameters:
        tree (etree.HTML)

        Returns:
        list[str]: list of PTT article link
        list[str]: list of PTT article id
        """
        link_xpath = '//*[@id="main-container"]/div[2]/div/div[2]/a'
        article_id_pattern = "/bbs/.*?/(.*?)\.html"
        article_links = list()
        article_ids = list()
        # loop and store all article link
        for node in tree.xpath(link_xpath):
            href = node.get("href")
            article_ids.append(re.search(article_id_pattern, href).group(1))
            article_links.append(f"{Crawler.PTT_URL}{href}")

        # return article links
        return article_links, article_ids

    # part 3. get article content
    async def __get_article_content(self, article_links: list[str]) -> list[str]:
        """
        Get article content from link

        Parameters:
        article_links (list[str]): list of PTT article link

        Returns:
        list[str]: list of PTT article content
        """
        # get event loop
        event_loop = asyncio.get_event_loop()

        # list all task
        tasks = [event_loop.create_task(self.get_url_data(link)) for link in article_links]

        content_list = list()

        # waiting all tasks to be done
        for task in tasks:
            result = await task
            content_list.append(result)

        # return article links
        return content_list

    # part 4. filter article content
    def __filter_article_content(self, article_content: list[str], article_ids: list[str]) -> PTTData:
        """
        Get author, title, post-time, content, comment in article

        Parameters:
        article_content (list[str]): list of PTT article content
        article_ids (list[str]): list of PTT article id

        Returns:
        PTTData
        """
        ptt_data = PTTData()
        main_content_xpath = '//*[@id="main-content"]'

        article_xpath_dict = {
            "author": '//*[@id="main-content"]/div[1]',
            "board": '//*[@id="main-content"]/div[2]',
            "title": '//*[@id="main-content"]/div[3]',
            "post_time": '//*[@id="main-content"]/div[4]',
        }
        comment_xpath_dict = {
            "comment": "//div[@class='push']",
            "push_tag": "//div[@class='push']/span[1]",
            "push_user_id": "//div[@class='push']/span[2]",
            "push_content": "//div[@class='push']/span[3]",
            "push_ip_date_time": "//div[@class='push']/span[4]",
        }
        re_pattern_dict = {
            "ip_address": "([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)",
        }
        comment_ip_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        comment_datetime_pattern = r"(\d{,2}/\d{,2} \d{,2}:\d{,2})"
        # loop content and extract useful information
        for article_id, content in zip(article_ids, article_content):
            lxml_tree = etree.HTML(content).xpath(main_content_xpath)[0]

            article_data = dict()
            # skip data if it is incomplete.
            try:
                for key, value in article_xpath_dict.items():
                    article_data[key] = lxml_tree.xpath(value)[0].xpath("span")[1].text
            except IndexError as IE:
                continue

            # get author
            full_name = article_data["author"][:-1].split(" (")
            user_id, user_name = full_name[0], full_name[0] if len(full_name) != 2 else full_name[1]
            # get board
            board = article_data["board"]
            # get title
            title = article_data["title"]
            # get post date
            try:
                post_time = datetime.strptime(article_data["post_time"].replace(" ", "|").replace("||", "|0"), "%a|%b|%d|%H:%M:%S|%Y")
            except ValueError as VE:
                previous_time = ptt_data.get_last_article()
                # skip data if it is incomplete.
                if previous_time is None:
                    continue
                post_time = previous_time.post_time + timedelta(seconds=1)

            # get comment
            comment_list = []
            comment_data = [
                range(len(lxml_tree.xpath(comment_xpath_dict["comment"]))),
                lxml_tree.xpath(comment_xpath_dict["push_tag"]),
                lxml_tree.xpath(comment_xpath_dict["push_user_id"]),
                lxml_tree.xpath(comment_xpath_dict["push_content"]),
                lxml_tree.xpath(comment_xpath_dict["push_ip_date_time"]),
            ]
            for idx, push_tag, push_user_id, push_content, push_ip_date_time in zip(*comment_data):
                _push_tag = push_tag.text
                _push_user_id = push_user_id.text
                _push_content = push_content.text
                _push_ip_date_time = re.sub("[\n]", "", push_ip_date_time.text)
                _push_ip = re.search(comment_ip_pattern, _push_ip_date_time)
                _push_ip = _push_ip.group(1) if _push_ip else ""
                try:
                    _push_date_time = datetime.strptime(
                        str(post_time.year) + "/" + re.search(comment_datetime_pattern, _push_ip_date_time).group(1), "%Y/%m/%d %H:%M"
                    )
                except:
                    _push_date_time = None

                # append into ptt_data
                comment = Comment(article_id, _push_tag, _push_user_id, idx, _push_content, _push_date_time, _push_ip)
                ptt_data.append(comment)
                comment_list.append(comment)

            # get context
            # remove all comments, leave only article context
            delete_flag = False
            for i in lxml_tree.xpath("./*"):
                if i.get("class") == "f2":
                    delete_flag = True
                if delete_flag:
                    i.getparent().remove(i)
            context_xpath = "//div[@class='article-metaline'][3]/following-sibling::text()"
            context_list = lxml_tree.xpath(context_xpath)
            # remove all \n, \t
            context = "".join(map(lambda x: re.sub(r"[\s\t]", "", x), context_list))
            # get ip
            ip_address = re.search(re_pattern_dict["ip_address"], content).group(1)

            # append into ptt_data
            article = Article(article_id, title, user_id, user_name, board, post_time, context, ip_address, comment_list)
            ptt_data.append(article)
        return ptt_data


def main():
    pass


if __name__ == "__main__":
    main()
