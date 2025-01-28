from unittest.mock import patch

import pandas as pd
import pytest

from plotter import Plotter


@pytest.fixture
def sample_dataframe():
    """Fixture to provide sample DataFrame for testing."""
    data = {
        "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "title": ["Article A", "Article B", "Article A"],
        "views": [100, 200, 300],
    }
    return pd.DataFrame(data)


@pytest.fixture
def plotter(sample_dataframe):
    """Fixture to initialize Plotter instance."""
    return Plotter(sample_dataframe)


def test_prepare_data(plotter):
    """Test the internal data preparation method."""
    plotter._prepare_data()

    pivot_df = plotter.pivot_df
    assert pivot_df is not None
    assert "Article A" in pivot_df.columns
    assert "Article B" in pivot_df.columns
    assert 100 in pivot_df["Article A"].values
    assert 200 in pivot_df["Article B"].values

    # Assert calculated summary statistics
    assert plotter.overall_mean_views > 0
    assert plotter.max_views_overall == 300
    assert plotter.unique_articles_count == 2


@patch("matplotlib.pyplot.savefig")
def test_plot_top_articles(mock_savefig, plotter):
    """Test the plot_top_articles method."""
    output_file = "test_output.png"

    plotter.plot_top_articles(output_file)

    mock_savefig.assert_called_once_with(output_file)


@patch("matplotlib.pyplot.savefig")
def test_plot_with_missing_dates(mock_savefig):
    data = {
        "date": pd.to_datetime(["2023-01-01", "2023-01-03"]),
        "title": ["Article A", "Article B"],
        "views": [100, 200],
    }
    df = pd.DataFrame(data)
    plotter = Plotter(df)

    plotter.plot_top_articles("missing_dates.png")

    assert plotter.pivot_df.index.min() == pd.Timestamp("2023-01-01")
    assert plotter.pivot_df.index.max() == pd.Timestamp("2023-01-03")
    assert plotter.pivot_df.loc["2023-01-02"].sum() == 0  # Missing date filled with 0

    mock_savefig.assert_called_once_with("missing_dates.png")
