from datetime import datetime

import pandas as pd

from .model import Article, Comment


class PTTData:
    # initial PTTData object
    def __init__(self) -> None:
        self.__article_list: list[Article] = list()
        self.__comment_list: list[Comment] = list()

    # append data into list
    def append(self, obj: Article | Comment) -> None:
        """
        append data into PTTData, only accept Article and Comment object

        Parameters:
        obj (Article | Comment): data need to be append

        Returns:
        None
        """
        # check obj's instance
        if isinstance(obj, Article):
            self.__article_list.append(obj)
        elif isinstance(obj, Comment):
            self.__comment_list.append(obj)
        else:
            raise TypeError(f"Can't append {type(obj)}. Only accept <class 'Article'> or <class 'Comment'>.")

    # return article as dataframe
    def get_article_dataframe(self) -> pd.DataFrame:
        article_field = self.__article_list[0].article_field
        df_article = pd.DataFrame(data=self.get_article_list(), columns=article_field)
        return df_article

    # return comment as dataframe
    def get_comment_dataframe(self) -> pd.DataFrame:
        comment_field = self.__comment_list[0].comment_field
        df_comment = pd.DataFrame(data=self.get_comment_list(), columns=comment_field)
        return df_comment

    # return article as list
    def get_article_list(self) -> list:
        article_list = list()
        for idx, article in enumerate(self.__article_list):
            article_list.append(article.to_list())
        return article_list

    # return article as list
    def get_comment_list(self) -> list:
        comment_list = list()
        print(len(self.__comment_list))
        for idx, comment in enumerate(self.__comment_list):
            comment_list.append(comment.to_list())
        return comment_list

    # get origin list of Article
    def get_article(self) -> list[Article]:
        return self.__article_list

    # get origin list of Comment
    def get_comment(self) -> list[Comment]:
        return self.__comment_list

    # return article as dictionary (contain comment)
    def get_article_dict(self) -> list[dict]:
        article_dict = list()
        for article in self.__article_list:
            article_dict.append(article.to_dict())
        return article_dict

    # return comment as dictionary
    def get_comment_dict(self) -> list[dict]:
        comment_dict = list()
        for comment in self.__comment_list:
            comment_dict.append(comment.to_dict())
        return comment_dict

    # update self's data by another PTTData
    def update(self, ptt_data: "PTTData") -> None:
        for article in ptt_data.get_article():
            self.append(article)

        for comment in ptt_data.get_comment():
            self.append(comment)

    # return last element in article list
    def get_last_article(self) -> Article:
        if len(self.__article_list) == 0:
            return None
        return self.__article_list[-1]

    # return last element in article comment
    def get_last_comment(self) -> Comment:
        if len(self.__comment_list) == 0:
            return None
        return self.__comment_list[-1]

    # return all article date
    def get_date_from_article(self) -> list[datetime]:
        date_list = list()
        for article in self.__article_list:
            date = article.post_time.replace(hour=0, minute=0, second=0, microsecond=0)
            if date not in date_list:
                date_list.append(date)
        return date_list

    def delete_data_by_date(self, start_time: datetime, end_time: datetime) -> None:
        pos = 0
        while pos < len(self.__article_list):
            time = self.__article_list[pos].post_time
            if time < start_time or time > end_time:
                del self.__article_list[pos]
            else:
                pos += 1
        self.__article_list.sort(key=lambda x: x.post_time)

        del self.__comment_list
        self.__comment_list = list()
        for article in self.__article_list:
            self.__comment_list.extend(article.comment_list)


def main():
    ptt = PTTData()


if __name__ == "__main__":
    main()
