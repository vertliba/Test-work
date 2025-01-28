import argparse
import asyncio
import logging
from datetime import datetime, date
from data_processor import DataProcessor
from plotter import Plotter
from wiki_api_client.api_client import WikiApiClient, WikiApiClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main(start_date: date, end_date: date):
    api_client = WikiApiClient()
    logger.info("Fetching data from Wikimedia API...")
    try:
        articles = await api_client.fetch_top_articles_for_period(start_date, end_date)
    except WikiApiClientError as e:
        logger.error(f"Failed to fetch data: {e}")
        return
    finally:
        await api_client.close()

    logger.info("Processing data...")
    if not articles:
        logger.error("There are no articles data for the given period.")
        return
    df_all_months_top_articles = DataProcessor.top_article_views_stats_to_df(articles)
    df_period_top_articles = DataProcessor.filter_top_articles(df_all_months_top_articles)

    logger.info("Generating plot...")
    Plotter(df_period_top_articles).plot_top_articles()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and plot Wikipedia top article statistics.")
    parser.add_argument("start", type=str, help="Start date in YYYYMMDD format")
    parser.add_argument("end", type=str, help="End date in YYYYMMDD format")
    args = parser.parse_args()

    try:
        start_date = datetime.strptime(args.start, "%Y%m%d").date()
        end_date = datetime.strptime(args.end, "%Y%m%d").date()
    except ValueError:
        logger.error("Invalid date format. Please use YYYYMMDD.")
        exit(1)

    asyncio.run(main(start_date, end_date))
