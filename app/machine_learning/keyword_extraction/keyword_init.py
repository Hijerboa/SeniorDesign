import yake
from keybert import KeyBERT

kw_model = KeyBERT()

# YAKE keyword extraction parameters
language = "en"
max_ngram_size = 3
deduplication_thresold = 0.45
deduplication_algo = 'seqm'
windowSize = 3
numOfKeywords = 20

# get keywords
extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)