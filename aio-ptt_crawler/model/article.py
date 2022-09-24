from dataclasses import dataclass, field
from datetime import datetime
from .comment import Comment


@dataclass
class Article:
    article_id: str
    article_title: str
    user_id: str
    user_name: str
    board: str
    post_time: datetime
    context: str
    ip_address: str
    comment_list: list[Comment] = field(default_factory=list)
    article_field: list[str] = field(default_factory=list, init=False)
    data_list: list = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.article_field = [
            "article_id",
            "article_title",
            "user_id",
            "user_name",
            "board",
            "datetime",
            "context",
            "ip_address",
        ]
        self.data_list = [
            self.article_id,
            self.article_title,
            self.user_id,
            self.user_name,
            self.board,
            self.post_time,
            self.context,
            self.ip_address,
        ]

    # return all value as list(exclude comment_list)
    def to_list(self) -> list:
        return self.data_list

    # return all value as dict(include comment_list)
    def to_dict(self) -> dict:
        result = dict()
        for key, value in zip(self.article_field, self.data_list):
            result[key] = value
        result["comment_list"] = list()

        # add comment
        for comment in self.comment_list:
            result["comment_list"].append(comment.to_dict())

        # return data
        return result

    def __str__(self):
        return f"{self.article_id:=}, { self.article_title:=}, { self.user_id:=}, { self.user_name:=}, { self.board:=}, { self.post_time:=}, { self.context:=}, { self.ip_address:=}"


def main():
    pass


if __name__ == "__main__":
    main()
