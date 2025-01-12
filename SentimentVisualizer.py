import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime
import matplotlib.dates as mdates
from datetime import timedelta
import sys


global_fig, global_axs = plt.subplots(1, 1, figsize=(15, 8))

def plot_result(results, news_site, keyword, start_date="2018-01-01"):
    if len(results) == 0:
        print(f"Results of {news_site} when plotting for {keyword} were empty")
        sys.exit(1)

    # Set up a locator for every 4 months
    four_months = mdates.MonthLocator(interval=4)  # Tick every 4 months 
    dateFormat = "%Y-%m-%d %H:%M:%S"
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    # Set up y limits for plots
    y_min, y_max = -0.2, 0.2
    y_ticks = np.arange(y_min, y_max + 0.01, 0.05)  # Steps of 0.05 
    
    # Extract and process dates
    filtered_results = [
        result for result in results 
        if "date_publish" in result 
        and result["date_publish"] is not None 
        and datetime.datetime.strptime(result["date_publish"], dateFormat) >= start_date
    ]
    publishing_dates = np.vectorize(lambda result: result["date_publish"])(filtered_results)
    if not filtered_results:
        print("no results :(")
        return
    dates = np.array([datetime.datetime.strptime(d, dateFormat) for d in publishing_dates])
    
    # Sort data by dates
    sorted_indices = np.argsort(dates)
    dates = dates[sorted_indices]
    
    # Extract sentiment scores and sort them
    positive_scores = np.vectorize(lambda result: result["positive_result"])(filtered_results)
    negative_scores = np.vectorize(lambda result: result["negative_result"])(filtered_results)
    positive_scores = positive_scores[sorted_indices]
    negative_scores = negative_scores[sorted_indices]
    
    sentiment_diff = positive_scores - negative_scores
    x = np.arange(len(dates))

    diff_coef = np.polyfit(x, sentiment_diff, 15)
    diff_fn = np.poly1d(diff_coef)
    
    # Plot Monthly Article Counts (Histogram)
    # Normalize dates by stripping time precision
    dates = np.array([date.replace(hour=0, minute=0, second=0, microsecond=0) for date in dates])

    # Add to global plots for comparisons
    global_axs.plot(dates, diff_fn(x), label=news_site)

    global_axs.set_yticks(y_ticks)
    global_axs.set_ylim(y_min, y_max)


def show_plots(keyword):
    global_axs.legend()
    global_axs.grid(True)
    global_axs.set_title(f"Sentiment differneces for all news sites on {keyword}: Poly 15", fontsize=14)

    plt.show()