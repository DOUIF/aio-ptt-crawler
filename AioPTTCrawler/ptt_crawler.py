import asyncio
import re
from datetime import datetime, timedelta

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
    def get_board_articles(self, board: str, start_index: int, end_index: int, show_progress=True) -> PTTData:
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

        # ensure index won't out of boundary
        start_index = max(1, start_index)
        end_index = min(self.get_latest_index(board), end_index)

        if show_progress:
            print(f"Start to crawl page {start_index} ~ {end_index}")

        sem = asyncio.Semaphore(50)

        # list all crawler
        crawlers = [Crawler(board, i) for i in range(start_index, end_index + 1)]
        # list all tasks
        tasks = [crawler.get_specific_page_data(sem, show_progress) for crawler in crawlers]

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

    # get article by datetime range
    def get_article_by_datetime(self, board: str, start_time: datetime, end_time: datetime) -> PTTData:
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=0)

        print("Start to find target date range")
        start_index = self._search_page_date(board, start_time - timedelta(days=1))
        end_index = self._search_page_date(board, end_time + timedelta(days=1))
        print(f"Found target date range. roughly location in {start_index} ~ {end_index}")

        ptt_data = self.get_board_articles(board, start_index, end_index, show_progress=False)

        print("Filter and sort article by date")
        ptt_data.delete_data_by_date(start_time, end_time)

        return ptt_data

    def _search_page_date(self, board: str, date: datetime) -> int:
        start_index = 1
        last_index = self.get_latest_index(board)
        while start_index <= last_index:
            mid = (start_index + last_index) // 2
            ptt_data = self.get_board_articles(board, mid, mid, show_progress=False)
            date_list = ptt_data.get_date_from_article()
            # print(start_time, end_time, mid, date_list)
            if date > date_list[0]:
                start_index = mid + 1
            elif date < date_list[0]:
                last_index = mid - 1
            else:
                break
        return mid


def main():
    BOARD = "Gossiping"
    ptt_crawler = AioPTTCrawler()
    ptt_data = ptt_crawler.get_board_latest_articles(board=BOARD, page_count=100)
    d = ptt_data.get_article_dict()
    print(d)


if __name__ == "__main__":
    main()
