from datetime import date, datetime

import pytest

from main import main
from wiki_api_client.api_client import WikiApiClient
from wiki_api_client.types import TopArticleViewStats, TopArticlesViewStats
from wiki_api_client.api_client import WikiApiClientError

start_date = datetime.strptime("20250101", "%Y%m%d").date()
end_date = datetime.strptime("20250125", "%Y%m%d").date()


@pytest.mark.asyncio
async def test_main_success(mocker):
    """Test successful execution of the main function."""
    # Mock API client's methods
    mock_api_client = mocker.AsyncMock(WikiApiClient)
    mock_api_client.fetch_top_articles_for_period.return_value = [
        TopArticlesViewStats(
            date=date(2025, 1, 25),
            articles=[
                TopArticleViewStats(title="Article A", views=100),
                TopArticleViewStats(title="Article B", views=200),
            ],
        )
    ]
    # Mock WikiApiClient, DataProcessor, and Plotter
    mocker.patch("main.WikiApiClient", return_value=mock_api_client)
    mock_filter_top_articles = mocker.patch("main.DataProcessor.filter_top_articles", return_value="filtered_df")
    mock_plotter = mocker.patch("main.Plotter")
    mock_plotter_instance = mock_plotter.return_value

    await main(start_date, end_date)

    # Check API client method calls
    mock_api_client.fetch_top_articles_for_period.assert_called_once_with(start_date, end_date)
    mock_api_client.close.assert_called_once()
    # Check DataProcessor calls
    assert mock_filter_top_articles.called
    # Check Plotter method calls
    mock_plotter.assert_called_once_with("filtered_df")
    assert mock_plotter_instance.plot_top_articles.called


@pytest.mark.asyncio
async def test_main_no_data_from_api(mocker, caplog):
    """Test main function with no data returned from API."""
    mock_api_client = mocker.AsyncMock(WikiApiClient)
    mock_api_client.fetch_top_articles_for_period.return_value = []
    mocker.patch("main.WikiApiClient", return_value=mock_api_client)

    with caplog.at_level("ERROR"):
        await main(start_date, end_date)

    assert "There are no articles data for the given period." in caplog.text


@pytest.mark.asyncio
async def test_main_api_failure(mocker, caplog):
    """Test main function when API client raises an exception."""
    mock_api_client = mocker.AsyncMock(WikiApiClient)
    mock_api_client.fetch_top_articles_for_period.side_effect = WikiApiClientError()
    mocker.patch("main.WikiApiClient", return_value=mock_api_client)

    with caplog.at_level("ERROR"):
        await main(start_date, end_date)

    assert "Failed to fetch data:" in caplog.text
