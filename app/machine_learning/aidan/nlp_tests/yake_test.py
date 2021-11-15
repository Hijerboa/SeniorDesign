import yake
from common import get_text

text = get_text()

max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1

kw_extractor = yake.KeywordExtractor(n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, features=None)
keywords = kw_extractor.extract_keywords(text)

for kw in keywords:
    print(f'{round(kw[1], 7)} | {kw[0]}')