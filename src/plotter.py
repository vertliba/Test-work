import logging
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)


class Plotter:
    df: pd.DataFrame
    pivot_df: pd.DataFrame
    overall_mean_views: float
    max_views_overall: int
    unique_articles_count: int

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the Plotter with the provided DataFrame.
        :param df: DataFrame containing columns ['date', 'title', 'views'].
        """
        self.df = df

    def plot_top_articles(self, output_file: str = "top_articles.png"):
        """
        Plot a graph showing the views of top articles over time and save it as an image file.
        :param output_file: Name of the file to save the plot.
        """
        self._prepare_data()

        title = (
            f"Top Wiki Articles\n"
            f"(Mean Views: {self.overall_mean_views:.2f}, "
            f"Max Views: {self.max_views_overall}, "
            f"Unique Articles: {self.unique_articles_count})"
        )

        plt.figure(figsize=(12, 8))
        for article in self.pivot_df.columns:
            article_data = self.pivot_df[article]
            plt.plot(article_data.index, article_data.values, label=article)

        plt.yscale("log")
        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel("Views (log scale)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_file)

        logger.info(f"Plot saved as '{output_file}'.")

    def _prepare_data(self):
        """
        Prepare data for the plot and calculate relevant statistics.
        """
        # Define the complete date range to fill missing dates with zero views
        full_date_range = pd.date_range(start=self.df["date"].min(), end=self.df["date"].max())

        # Pivot the DataFrame to reshape data for plotting
        self.pivot_df = self.df.pivot_table(index="date", columns="title", values="views", fill_value=0)
        self.pivot_df = self.pivot_df.reindex(full_date_range, fill_value=0)
        self.pivot_df.index.name = "date"

        # Calculate statistics
        views_sum = self.pivot_df.sum()
        # noinspection PyUnresolvedReferences
        views_count = (self.pivot_df > 0).sum()
        mean_views_per_article = views_sum / views_count

        self.overall_mean_views = mean_views_per_article.mean()
        self.max_views_overall = self.pivot_df.max().max()
        self.unique_articles_count = len(self.pivot_df.columns)

        logger.info(f"Mean Views Per Article: {self.overall_mean_views:.2f}")
        logger.info(f"Max Views Overall: {self.max_views_overall}")
        logger.info(f"Unique Articles Count: {self.unique_articles_count}")
