# lester
Python: 3.10.4

# article_finder.py (crawler)
    python ./article_finder.py <keyword> <amount of articles e.g. 500>


# sentiment_analyzer.py (sentiment analyzer and plotter)
    python ./sentiment_analyzer.py <keyword>
    
optional arguments:

- offline
- cache
- all / <newssite e.g. sabc>

Example: 

    python ./sentiment_analyzer.py trees cache sabc

| Keyword      | Description |
| ----------- | ----------- |
| offline      | Will not download any articl       |
| cache   | When set, no articles will be analyzed but the stored results will be used        |
| all   | All known newssites articles will be analyzed        |
| <newssite>   | Just this ONE newssite will ne analyzed        |

offline: Will not download any articles
cache: When set, no articles will be analyzed but the stored results will be used
all: All known newssites articles will be analyzed
\<newssite\>: Just this ONE newssite will ne analyzed