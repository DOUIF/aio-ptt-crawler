import asyncio
import re

import requests
from .crawler import Crawler
from .ptt_data import PTTData


class AioPTTCrawler:
    # class variable
    PTT_URL: str = "https://www.ptt.cc"
    COOKIES: dict[str:str] = {"over18": "1"}

    # initial PTTCrawler object
    def __init__(self) -> None:
        pass

    # get newest pages from ptt board
    def get_board_latest_articles(self, board: str, page_count: int = 10) -> PTTData:
        """
        Getting PTT board's articles with amount of pages.

        Parameters:
        board (str): PTT board's name
        page_count (int): amount of pages.

        Returns:
        PTTData: custom class to store data from PTT
        """
        # get latest page number
        end_index = self.get_latest_index(board)
        # calculate start page number
        start_index = end_index - page_count + 1

        # return PTTData
        return self.get_board_articles(board, start_index, end_index)

    # get articles by range of index
    def get_board_articles(self, board: str, start_index:int ,end_index:int) -> PTTData:
        """
        Getting PTT board's articles with amount of pages.

        Parameters:
        board (str): PTT board's name
        start_index (int): start index.
        end_index (int): end index.

        Returns:
        PTTData: custom class to store data from PTT
        """
        # create async event loop
        self.event_loop = asyncio.get_event_loop()
        # list all crawler
        crawlers = [Crawler(board, i) for i in range(start_index, end_index + 1)]
        # list all tasks
        tasks = [crawler.get_specific_page_data() for crawler in crawlers]
        # run tasks and get the results
        results: list[PTTData] = self.event_loop.run_until_complete(asyncio.gather(*tasks))

        # release memory
        del crawlers, tasks

        ptt_data = PTTData()
        for sub_ptt_data in results:
            if sub_ptt_data:
                ptt_data.update(sub_ptt_data)
        return ptt_data

    # get latest page index from ptt board
    def get_latest_index(self, board: str) -> int:
        # board's index.html always point to the newest page.
        content = requests.get(
            url=f"{AioPTTCrawler.PTT_URL}/bbs/{board}/index.html",
            cookies=AioPTTCrawler.COOKIES,
        ).content.decode("utf-8")

        # search for the previous page number.
        previous_page = re.search(f'href="/bbs/{board}/index(\d+).html">&lsaquo;', content)

        # check if there is latest page in this board.
        if previous_page is None:
            raise ValueError(f"Can't get board:<{board}>'s latest page index.")

        # return latest page number
        return int(previous_page.group(1)) + 1


def main():
    BOARD = "Gossiping"
    ptt_crawler = AioPTTCrawler()
    ptt_data = ptt_crawler.get_board_latest_articles(board=BOARD, page_count=1)
    d = ptt_data.get_article_dict()
    print(d)


if __name__ == "__main__":
    main()
