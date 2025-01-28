import pandas as pd
import logging
from wiki_api_client.types import TopArticlesViewStats

logger = logging.getLogger(__name__)


class DataProcessor:
    @staticmethod
    def top_article_views_stats_to_df(top_articles_view_stats: list[TopArticlesViewStats]) -> pd.DataFrame:
        """
        Converts a list of TopArticlesViewStats responses into a single pandas DataFrame.

        :param top_articles_view_stats: List of TopArticlesViewStats objects.
        :return: A pandas DataFrame containing all articles' data.
        """
        articles_dataframes = []
        for day_view_stats in top_articles_view_stats:
            try:
                day_view_stats_df = pd.DataFrame(
                    [{
                        "title": article.title,
                        "views": article.views,
                        "date": day_view_stats.date
                    } for article in day_view_stats.articles]
                )
                articles_dataframes.append(day_view_stats_df)
            except Exception as e:
                logger.error(f"Error processing articles data: {e}")
                raise

        all_data = pd.concat(articles_dataframes, ignore_index=True)
        return all_data

    @staticmethod
    def filter_top_articles(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """
        Get all data for the top N articles by views on the last day in the date range.

        :param df: A pandas DataFrame containing article data.
        :param top_n: The number of top articles to return.
        :return: A pandas DataFrame containing all data for the top articles.
        """
        try:
            last_day = df["date"].max()
            last_day_data = df[df["date"] == last_day]
            top_articles = last_day_data.nlargest(top_n, "views")["title"]

            filtered_df = df[df["title"].isin(top_articles)]

            return filtered_df
        except Exception as e:
            logger.error(f"Error while filtering top articles: {e}")
            raise
