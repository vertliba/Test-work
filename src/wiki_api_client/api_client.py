import asyncio
import json

import aiohttp
import logging
from datetime import date, timedelta
from wiki_api_client.types import TopArticlesViewStats, TopArticleViewStats

logger = logging.getLogger(__name__)


class WikiApiClientError(Exception):
    pass


class WikiApiClient:
    API_BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/"
    HEADERS = {"User-Agent": "WikiStatsAsyncParser/1.0"}
    ENDPOINTS = dict(
        top_articles="pageviews/top/{project}/{access}/{year}/{month}/{day}"
    )
    TIMEOUT = 60
    MAX_CONCURRENT_REQUESTS = 100

    def __init__(self, project="en.wikipedia", access="all-access", session=None):
        """
        Initializes the API client for Wikimedia with default settings.
        :param project: Project, defaults to "en.wikipedia"
        :param access: Access type, defaults to "all-access"
        :param session: Optional aiohttp session to be reused

        Cautions:
            - Api client should be closed after use by calling the close method.
            - You should not change the event loop policy after creating the client,
              because session will not be closed properly.
        """
        self.project = project
        self.access = access
        self.common_kwargs = dict(project=self.project, access=self.access)
        self.session_provided = session is not None
        if session:
            self.session = session
        else:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)

        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)

    async def _get_url(self, endpoint, date: date = None, **kwargs):
        """
        Generate the URL and fetch data from the API.
        :param endpoint: API endpoint to fetch data from
        :param date: Date for which the request is being made (year, month, day).
                     If omitted, requires explicit parameters in kwargs.
        :param kwargs: Additional arguments for URL formatting
        :return: Parsed JSON response or raises an exception on failure
        """
        if date:
            kwargs.update(dict(year=date.year, month=date.month, day=date.day))
        url = self.API_BASE_URL + endpoint.format(**self.common_kwargs, **kwargs)

        async with self.semaphore:
            async with self.session.get(url, headers=self.HEADERS) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_message = f"Error fetching data from {url}: {response.status}, {await response.text()}"
                    logger.error(error_message)
                    raise WikiApiClientError(error_message)

    async def fetch_top_articles(self, date: date) -> TopArticlesViewStats:
        """
        Fetch the top articles for a specific date.
        :param date: Date for which to fetch top articles
        :return: TopArticlesResponse or raises an exception if there was an error

        Example of API response format:
        ```
        {
          "items": [
            {
              "access": "all-access",
              "articles": [
                {
                  "article": "Main_Page",
                  "rank": 1,
                  "views": 4565816
                }
              ],
              "day": "01",
              "month": "01",
              "project": "en.wikipedia",
              "year": "2023"
            }
          ]
        }
        ```
        """
        response_data = await self._get_url(self.ENDPOINTS["top_articles"], date=date)
        try:
            items = response_data["items"][0]  # API response structure
            articles = [
                TopArticleViewStats(title=article["article"], views=article["views"])
                for article in items["articles"]
            ]
            return TopArticlesViewStats(date=date, articles=articles)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse response: {e}")
            raise WikiApiClientError("Failed to parse response")

    async def fetch_top_articles_for_period(self, start_date: date, end_date: date) -> list[TopArticlesViewStats]:
        tasks = [self.fetch_top_articles(date) for date in self._date_range(start_date, end_date)]
        return await asyncio.gather(*tasks)

    def _date_range(self, start_date: date, end_date: date):
        """
        Generate a range of dates.
        :param start_date: Start date of the range
        :param end_date: End date of the range
        :return: An iterator of dates
        """
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    async def close(self):
        """
        Close the aiohttp session.
        Should be called if the client created its own session.
        """
        if not self.session_provided:
            await self.session.close()
