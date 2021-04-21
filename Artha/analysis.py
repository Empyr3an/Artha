from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def get_polarity(text):
    return analyzer.polarity_scores(text)


def print_polarity(text):
    vs = get_polarity(text)
    print("{:-<65} {}\n\n".format(text, str(vs)))
