import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime
import matplotlib.dates as mdates
from datetime import timedelta
import sys


global_fig, global_axs = plt.subplots(2, 1, figsize=(11, 8))

def plot_result(results, news_site, keyword, max_poly=15, start_date="2018-01-01"):
    if len(results) == 0:
        print(f"Results of {news_site} when plotting for {keyword} were empty")
        sys.exit(1)

    # Set up a locator for every 4 months
    four_months = mdates.MonthLocator(interval=4)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    # Extract and process dates
    filtered_results = [
        result for result in results 
        if "date_publish" in result 
        and result["date_publish"] is not None 
        and datetime.datetime.strptime(result["date_publish"], dateFormat) >= start_date
    ]
    publishing_dates = np.vectorize(lambda result: result["date_publish"])(filtered_results)
    if not filtered_results:
        print("No results :(")
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

    # Create a grid of subplots
    n_cols = 4  # Number of columns in the grid
    n_rows = (max_poly + n_cols - 1) // n_cols  # Compute rows based on total poly degrees
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(19, 12))
    axs = axs.flatten()  # Flatten the axes for easier indexing

    for poly_value in range(max_poly + 1):
        diff_coef = np.polyfit(x, sentiment_diff, poly_value)
        diff_fn = np.poly1d(diff_coef)

        ax = axs[poly_value]
        ax.plot(dates, sentiment_diff, label="Sentiment Difference", color="orange", marker='s')
        ax.plot(dates, diff_fn(x), linestyle="dashed", color="black", label=f"Poly {poly_value}")
        ax.set_title(f"Sentiment Difference (Poly {poly_value})", fontsize=10)
        ax.set_ylabel("Difference Score", fontsize=8)
        ax.set_xlabel("Publishing Date", fontsize=8)
        ax.legend(fontsize=8)
        ax.grid(True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(four_months)
        ax.tick_params(axis="x", rotation=45)
        ax.set_xlim(dates[0] - timedelta(days=3), dates[-1])  # Set x-axis limits

    # Hide unused subplots if any
    for i in range(max_poly + 1, len(axs)):
        fig.delaxes(axs[i])

    plt.tight_layout()
    plt.show()



def show_plots(keyword):
    global_axs[0].legend()
    global_axs[0].grid(True)
    global_axs[0].set_title(f"Sentiment differneces for all news sites on {keyword}: Poly 10", fontsize=14)
    
    global_axs[1].legend()
    global_axs[1].grid(True)
    global_axs[1].set_title(f"Sentiment differneces for all news sites on {keyword}: Poly 1", fontsize=14)
    
    plt.show()