import pytest
from datetime import date
from aioresponses import aioresponses

from wiki_api_client.api_client import WikiApiClient, WikiApiClientError
from wiki_api_client.types import TopArticlesViewStats, TopArticleViewStats


@pytest.mark.asyncio
async def test_fetch_top_articles_success():
    """Test fetch_top_articles method with a successful response."""
    test_date = date(2025, 1, 25)
    expected_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/top/en.wikipedia/all-access/2025/1/25"
    )
    mock_response = {
        "items": [
            {
                "access": "all-access",
                "articles": [
                    {"article": "Test_Article1", "rank": 1, "views": 1500},
                    {"article": "Test_Article2", "rank": 2, "views": 800},
                ],
                "day": "25",
                "month": "1",
                "project": "en.wikipedia",
                "year": "2025",
            }
        ]
    }

    with aioresponses() as m:
        m.get(expected_url, payload=mock_response)

        client = WikiApiClient()
        result = await client.fetch_top_articles(test_date)
        await client.close()

        assert isinstance(result, TopArticlesViewStats)
        assert result.date == test_date
        assert len(result.articles) == 2
        assert result.articles[0] == TopArticleViewStats(title="Test_Article1", views=1500)
        assert result.articles[1] == TopArticleViewStats(title="Test_Article2", views=800)


@pytest.mark.asyncio
async def test_fetch_top_articles_api_error(caplog):
    """Test fetch_top_articles when the API returns a non-200 status code."""
    test_date = date(2025, 1, 25)
    expected_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/top/en.wikipedia/all-access/2025/1/25"
    )
    with aioresponses() as m:
        m.get(expected_url, status=500)

        # Run the test
        client = WikiApiClient()
        with pytest.raises(WikiApiClientError, match="Error fetching data from"):
            await client.fetch_top_articles(test_date)
        await client.close()

        assert any("Error fetching data from" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_fetch_top_articles_invalid_response(caplog):
    """Test fetch_top_articles with an invalid API response."""
    test_date = date(2025, 1, 25)
    expected_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/top/en.wikipedia/all-access/2025/1/25"
    )

    invalid_response = {"unexpected_key": "unexpected_value"}

    with aioresponses() as m:
        m.get(expected_url, payload=invalid_response)

        # Run the test
        client = WikiApiClient()
        with pytest.raises(WikiApiClientError, match="Failed to parse response"):
            await client.fetch_top_articles(test_date)
        await client.close()

        assert any("Failed to parse response" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_fetch_top_articles_for_period_success():
    """Test fetch_top_articles_for_period with multiple dates."""
    start_date = date(2025, 1, 24)
    end_date = date(2025, 1, 25)

    base_url = "https://wikimedia.org/api/rest_v1/metrics/"
    mock_responses = {
        f"{base_url}pageviews/top/en.wikipedia/all-access/2025/1/24": {
            "items": [
                {
                    "access": "all-access",
                    "articles": [
                        {"article": "Test_Article1", "rank": 1, "views": 1000},
                    ],
                    "day": "24",
                    "month": "1",
                    "year": "2025",
                }
            ]
        },
        f"{base_url}pageviews/top/en.wikipedia/all-access/2025/1/25": {
            "items": [
                {
                    "access": "all-access",
                    "articles": [
                        {"article": "Test_Article2", "rank": 1, "views": 1500},
                    ],
                    "day": "25",
                    "month": "1",
                    "year": "2025",
                }
            ]
        },
    }

    with aioresponses() as m:
        for url, response in mock_responses.items():
            m.get(url, payload=response)

        # Run the test
        client = WikiApiClient()
        result = await client.fetch_top_articles_for_period(start_date, end_date)
        await client.close()

        assert len(result) == 2
        assert result[0].date == date(2025, 1, 24)
        assert result[1].date == date(2025, 1, 25)
        assert result[0].articles[0].title == "Test_Article1"
        assert result[1].articles[0].title == "Test_Article2"


@pytest.mark.asyncio
async def test_date_range():
    """Test the internal _date_range method."""
    start_date = date(2025, 1, 24)
    end_date = date(2025, 1, 26)

    client = WikiApiClient()
    dates = list(client._date_range(start_date, end_date))
    await client.close()

    assert dates == [
        date(2025, 1, 24),
        date(2025, 1, 25),
        date(2025, 1, 26),
    ]
