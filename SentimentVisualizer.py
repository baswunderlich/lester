import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime
import matplotlib.dates as mdates
from datetime import timedelta
import sys


global_fig, global_axs = plt.subplots(2, 1, figsize=(11, 8))

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

    diff_coef = np.polyfit(x, sentiment_diff, 10)
    diff_fn = np.poly1d(diff_coef)

    diff_coef_02 = np.polyfit(x, sentiment_diff, 1)
    diff_fn_02 = np.poly1d(diff_coef_02)

    diff_dates = dates  # Dates for the second plot remain the same
    
    # Set up the figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(11, 12))
    
    # Plot Positive and Negative Sentiments
    axs[0].plot(dates, positive_scores, label="Positive Sentiment", color="#0e7800", marker='o')
    axs[0].plot(dates, negative_scores, label="Negative Sentiment", color="#ed1103", marker='x')
    axs[0].set_title(f"Sentiment Analysis for {news_site} on {keyword} ({len(filtered_results)} articles)", fontsize=14)
    axs[0].set_ylabel("Sentiment Score", fontsize=12)
    axs[0].legend()
    axs[0].grid(True)
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axs[0].xaxis.set_major_locator(four_months)
    axs[0].tick_params(axis="x", rotation=45)
    axs[0].set_xlim(dates[0] - timedelta(days=3), dates[-1])  # Set x-axis limits
    
    # Plot Sentiment Difference
    axs[1].plot(diff_dates, sentiment_diff, label="Sentiment Difference", color="orange", marker='s')
    axs[1].plot(dates, diff_fn(x), linestyle="dashed", color="black")
    axs[1].set_title("Sentiment Difference", fontsize=14)
    axs[1].set_ylabel("Difference Score", fontsize=12)
    axs[1].set_xlabel("Publishing Date", fontsize=12)
    axs[1].legend()
    axs[1].grid(True)
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axs[1].xaxis.set_major_locator(four_months)
    axs[1].tick_params(axis="x", rotation=45)
    axs[1].set_xlim(dates[0] - timedelta(days=3), dates[-1])  # Set x-axis limits

    # Plot Monthly Article Counts (Histogram)
    # Normalize dates by stripping time precision
    dates = np.array([date.replace(hour=0, minute=0, second=0, microsecond=0) for date in dates])

    months = [date.replace(day=1) for date in dates]  # Normalize dates to the first day of the month
    unique_months, article_counts = np.unique(months, return_counts=True)

    axs[2].bar(unique_months, article_counts, width=20, color="#007acc")
    axs[2].set_title(f"Number of Articles Published Per Month for {news_site} on keyword {keyword}", fontsize=14)
    axs[2].set_ylabel("Article Count", fontsize=12)
    axs[2].set_xlabel("Month", fontsize=12)
    axs[2].grid(True)
    axs[2].xaxis.set_major_locator(four_months)
    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m')) # Format as "YYYY-MM"
    axs[2].tick_params(axis="x", rotation=45)
    axs[2].yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure y-axis labels are integers
    axs[2].set_xlim(unique_months[0] - timedelta(days=15), unique_months[-1] + timedelta(days=15))

    # Apply y limits to all plots
    axs[1].set_yticks(np.arange(-0.20, 0.3 + 0.01, 0.05))

    # Add to global plots for comparisons
    global_axs[0].plot(dates, diff_fn(x), label=news_site)
    global_axs[1].plot(dates, diff_fn_02(x), label=news_site)

    for ax in global_axs:
        ax.set_ylim(y_min, y_max)
        ax.set_yticks(y_ticks)

    # Adjust layout
    plt.tight_layout()


def show_plots(keyword):
    global_axs[0].legend()
    global_axs[0].grid(True)
    global_axs[0].set_title(f"Sentiment differneces for all news sites on {keyword}: Poly 10", fontsize=14)
    
    global_axs[1].legend()
    global_axs[1].grid(True)
    global_axs[1].set_title(f"Sentiment differneces for all news sites on {keyword}: Poly 1", fontsize=14)
    
    plt.show()