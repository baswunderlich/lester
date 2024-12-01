import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
from datetime import timedelta

global_fig, global_axs = plt.subplots(1, 1, figsize=(11, 5))

def plot_result(results, news_site):
    dateFormat = "%Y-%m-%d %H:%M:%S"

    # Extract and process dates
    filtered_results = [result for result in results if "date_published" in result and result["date_published"] is not None]
    publishing_dates = np.vectorize(lambda result: result["date_published"])(filtered_results)
    if not filtered_results:
        print("no reulsts :(")
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
    diff_dates = dates  # Dates for the second plot remain the same

    step = 30
    
    # Set up the figure with two subplots
    fig, axs = plt.subplots(2, 1, figsize=(11, 8))
    
    # Plot Positive and Negative Sentiments
    axs[0].plot(dates, positive_scores, label="Positive Sentiment", color="#0e7800", marker='o')
    axs[0].plot(dates, negative_scores, label="Negative Sentiment", color="#ed1103", marker='x')
    axs[0].set_title(f"Sentiment Analysis for {news_site} ({len(filtered_results)} articles)", fontsize=14)
    axs[0].set_ylabel("Sentiment Score", fontsize=12)
    axs[0].legend()
    axs[0].grid(True)
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axs[0].xaxis.set_major_locator(mdates.MonthLocator(interval=step))
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
    axs[1].xaxis.set_major_locator(mdates.MonthLocator(interval=step))
    axs[1].tick_params(axis="x", rotation=45)
    axs[1].set_xlim(dates[0] - timedelta(days=3), dates[-1])  # Set x-axis limits
    

    global_axs.plot(dates, diff_fn(x), label=news_site)
    # Adjust layout
    plt.tight_layout()


def show_plots():
    global_axs.legend()
    plt.show()