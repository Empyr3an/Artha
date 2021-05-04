#Artha


Social Media Information Verification

Artha - Sanskrit word for wealth and prosperity

This repo will aim to monitor various different financial information sources over the internet, and aggregate signals into easily actionable investment opportunities. It will start off with a trustrank implementation of twitter users, and eventually expand into other social medias.

The goals to start with are:

-   find reputable people to follow
-   implement pagerank from twitter data to identify most promising/reputable people to monitor
-   given list of data (from social media, this data can include a list of predictions over time), identify how well the data can predict financial time series.


To use the program, we first need to download data. After acquiring a Twitter API, you can set up your configuration and then in notebook/twitter_downloading.ipynb, download the following and tweets of various people. 

Then to process the data, you can do to notebooks/neodbinterface.ipynb, and then run all the cells and get a graph of the pagerank indicator versus price. To store the data, you need to setup a neo4j database, and set up its configuration so that it can load csvs