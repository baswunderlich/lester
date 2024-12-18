# lester
This is a tool for sentiment analysis on news sites

## Setup
Python: 3.10.4

## article_finder.py (crawler)
    python ./article_finder.py <keyword> <amount of articles e.g. 500> <newspage> <newspage> ...

Example: 

    python ./article_finder.py trees 300 all

this will fetch me 300 links to articles that contain the word tree from each known news site

Example: 

    python ./article_finder.py trees 300 sabc rferl

this will fetch me 300 links to articles that contain the word tree from sabc and rferl

currently supported news pages are:

- sabc
- rferl
- chinadaily
- moscowtimes
- spiegel
- moscowtimes
- tass
- cnn (does not work perfectly)
- kyiv post (keyword: kyiv)
- Folha de S.Paulo (keyword: folha)
  
the keyword 'all' will fetch results of all this pages

## sentiment_analyzer.py (sentiment analyzer and plotter)
    python ./sentiment_analyzer.py <keyword> <keyword> ...
    
optional arguments:

- offline
- cache
- all / \<newssite e.g. sabc\>

Example: 

    python ./sentiment_analyzer.py trees cache sabc

| Keyword      | Description |
| ----------- | ----------- |
| offline      | Will not download any articles       |
| cache   | When set, no articles will be analyzed but the stored results will be used        |
| all   | All known news sites articles will be analyzed        |
| \<news site\>   | Just the named newssites will be analyzed        |
