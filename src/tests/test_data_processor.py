from datetime import date

import pandas as pd
import pytest

from data_processor import DataProcessor
from wiki_api_client.types import TopArticleViewStats, TopArticlesViewStats


@pytest.fixture
def sample_view_stats():
    view_stats = [
        TopArticlesViewStats(
            date=date(2025, 1, 25),
            articles=[
                TopArticleViewStats(title="Article1", views=100),
                TopArticleViewStats(title="Article2", views=200),
            ]
        ),
        TopArticlesViewStats(
            date=date(2025, 1, 26),
            articles=[
                TopArticleViewStats(title="Article1", views=150),
                TopArticleViewStats(title="Article3", views=300),
            ]
        ),
    ]
    return view_stats


def test_top_article_views_stats_to_df(sample_view_stats):
    df = DataProcessor.top_article_views_stats_to_df(sample_view_stats)

    assert len(df) == 4
    assert set(df["title"]) == {"Article1", "Article2", "Article3"}
    assert df.iloc[0]["date"] == date(2025, 1, 25)
    assert df.iloc[0]["views"] == 100
    assert df["views"].sum() == 750


def test_top_article_views_stats_to_df_error_handling(caplog):
    # noinspection PyTypeChecker
    invalid_data = [
        TopArticlesViewStats(date=date(2025, 1, 25), articles="invalid")
    ]

    with pytest.raises(Exception):
        with caplog.at_level("ERROR"):
            DataProcessor.top_article_views_stats_to_df(invalid_data)

    assert any("Error processing articles data" in record.message for record in caplog.records)


def test_filter_top_articles(sample_view_stats):
    df = DataProcessor.top_article_views_stats_to_df(sample_view_stats)

    top_articles_df = DataProcessor.filter_top_articles(df, top_n=2)

    assert set(top_articles_df["title"]) == {"Article1", "Article3"}  # Top 2 articles on last day
    assert top_articles_df["views"].sum() == 550


def test_filter_top_articles_less_than_n(sample_view_stats):
    df = DataProcessor.top_article_views_stats_to_df(sample_view_stats)

    top_articles_df = DataProcessor.filter_top_articles(df, top_n=10)

    assert len(top_articles_df["title"].unique()) == 2


def test_filter_top_articles_error_handling_missing_column(caplog):
    invalid_df = pd.DataFrame({"title": ["Article1"], "views": [100]})
    with pytest.raises(Exception):
        DataProcessor.filter_top_articles(invalid_df, top_n=2)

    assert any("Error while filtering top articles" in record.message for record in caplog.records)
