from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Comment:
    article_id: str
    tag: str
    user_id: str
    comment_order: int
    context: str
    post_time: datetime
    ip_address: str
    comment_field: list[str] = field(default_factory=list, init=False)
    data_list: list = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.comment_field = [
            "article_id",
            "tag",
            "user_id",
            "comment_order",
            "context",
            "datetime",
            "ip_address",
        ]
        self.data_list = [self.article_id, self.tag, self.user_id, self.comment_order, self.context, self.post_time, self.ip_address]

    # return all value as dict
    def to_dict(self) -> dict:
        return_dict = dict()
        for key, value in zip(self.comment_field, self.data_list):
            return_dict[key] = value
        return return_dict

    # return all value as list
    def to_list(self) -> list:
        return


def main():
    pass


if __name__ == "__main__":
    main()
