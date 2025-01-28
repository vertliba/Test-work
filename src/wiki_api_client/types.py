import datetime
from dataclasses import dataclass
from typing import Any, List


@dataclass
class TopArticleViewStats:
    title: str
    views: int


@dataclass
class TopArticlesViewStats:
    date: datetime.date
    articles: List[TopArticleViewStats]
