# README

## Wikipedia Top Articles Viewer

This project provides a Python tool to fetch and visualize the top 1000 most viewed pages on the English Wikipedia for a specified date range. The tool processes the data, selects the most popular articles during the period, and generates a plot showing their view trends.

---

## Features

1. **Data Fetching**: Retrieves view statistics for the top articles using the Wikimedia API.
2. **Data Processing**: Filters the dataset to focus on a subset of top articles.
3. **Plot Generation**: Creates a plot illustrating the view trends of selected articles over time.
4. **Command-line Interface**: Easily run the script with a start and end date to analyze specific time periods.


## Usage

To fetch data and generate a plot:

```bash
cd src
python main.py <start_date> <end_date>
```

- `<start_date>` and `<end_date>` should be in the format `YYYYMMDD`.
- Example:

```bash
python main.py 20231210 20231231
```

---

## Improvements and Considerations

### 1. Retry Mechanism for API Requests
In real-world scenarios, network failures can occur. To improve reliability, the script could implement retry logic for API requests. This would ensure that temporary connection issues do not disrupt the data-fetching process.

### 2. Monthly Data Fetching Optimization
The Wikimedia API supports fetching data for an entire month by passing `all-days` instead of a specific day for the `day` parameter. Using this method could drastically reduce the number of API calls and speed up data retrieval. This optimization is not implemented in the current solution and could be added later.

### 3. Improved Article Selection Logic
The original script had an error in how it selected the top articles:
   - Articles were chosen based on their view counts on the last day they appeared in the fetched data, not on the last day of the overall period.
   - This could result in selecting articles that were only popular at the beginning of the range.
   
   **Fix**: In this implementation, articles are correctly selected based on their view counts on the last day of the server data.

### 4. Filling Missing Data
The original script used the following command to handle missing data:

```python
df["views"] = df["views"].fillna(0)
```

This caused incorrect results when articles were absent for parts of the date range, as absent articles would have the same view count as the last day they appeared. This issue is also fixed in the current implementation.

### 5. Average View Calculation
The original script calculated the average view count for each article by summing the views and dividing by the number of days. This approach is incorrect because it does not account for missing data.
In the current implementation, the average view count for each article is calculated using only the days where the article has data. Days with missing data are excluded from the calculation. While this approach prevents significant distortion, it might not be what the end user expects. The desired behavior should be discussed with the project stakeholders.

---

## Future Work

Here are some additional improvements that could be made in subsequent iterations:

1. **Interactive Visualizations**: Integrate libraries like Plotly or Dash to create interactive plots.
2. **Caching API Responses**: Prevent redundant API calls by storing responses locally for queries on overlapping date ranges.
3. **Full Performance Optimization**: Implement the `all-days` optimization for monthly summaries and explore parallel processing for faster data manipulation.

---

## Testing

This project includes comprehensive unit tests to ensure correctness and robustness. Tests can be run using:

```bash
pytest
```
