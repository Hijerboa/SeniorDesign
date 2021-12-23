# imports
from functools import reduce
from numpy.core.numeric import full
import yake
from keybert import KeyBERT

# list of keywords to exclude - WIP
bad_keywords = ["united states", "act", "section", "united", "states", "united states of america", "secretary", "federal", "federal government", "government", "congressional", "congress", "bill", "bills", "congress", "senate", "america", "state", "agency", "federal agency", "military", "spending", "healthcare"]

def cleanup(my_list: list):
    # remove confidence scores
    my_list = list(map(lambda x: x[0], my_list))
    
    # remove unuseful keywords
    my_list = [word for word in my_list if word not in bad_keywords]

    return my_list[:10] if len(my_list) > 9 else my_list


def remove_dups(my_list: list):
    """ Returns a set of tuples with unique first values (keyword) """
    
    unique_results = []
    for element in my_list:
        unique_words = list(map(lambda word: word[0], unique_results))
        if element[0] not in unique_words:
            unique_results.append(element)
    return unique_results


def yake_extraction(summary: str, full_text: str):
    # YAKE keyword extraction parameters
    language = "en"
    max_ngram_size = 3
    deduplication_thresold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 10
    
    # get keywords from summary
    summary_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
    summary_keywords = summary_extractor.extract_keywords(summary)

    # get keywords from full text
    full_text_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
    full_text_keywords = full_text_extractor.extract_keywords(full_text)
    
    # combine lists and sort by relevance score
    keywords = summary_keywords + full_text_keywords
    # sort to preserve keywords with higher relevance
    keywords.sort(key = lambda x: x[1])
    keywords = remove_dups(keywords)

    return cleanup(keywords)


def keybert_extraction(summary: str, full_text: str):
    kw_model = KeyBERT()

    n_gram_range = (1, 3)
    stop_words = 'english'
    top_n = 10
    # MMR (Maximal Marginal Relevance) | if set to true, diversity specifies how related the keywords are
    # For example, diversity of 0.8 may result in lower confidence but much more diverse words
    use_mmr = True
    diversity = 0.5
    
    summary_keywords = kw_model.extract_keywords(
        docs=summary, 
        keyphrase_ngram_range=n_gram_range, 
        stop_words=stop_words, 
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity)

    full_text_keywords = kw_model.extract_keywords(
        docs=full_text, 
        keyphrase_ngram_range=n_gram_range, 
        stop_words=stop_words, 
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity)

    # For keyBERT, we do 1 - x[1] in the sort method since highest confidence value is best
    keywords = summary_keywords + full_text_keywords
    keywords.sort(key = lambda x: 1 - x[1])
    keywords = remove_dups(keywords)
    
    return cleanup(keywords)


def get_keywords(summary: str, full_text: str):
    summary = summary.lower()
    full_text = full_text.lower()

    yake_keywords = yake_extraction(summary, full_text)
    keybert_keywords = keybert_extraction(summary, full_text)

    return list(set(yake_keywords + keybert_keywords))


import json
if __name__ == "__main__":
    data = json.load(open("./ian/tests/Sample_Bill_Data.txt"), strict=False)
    summary = data["3"]["summary"].replace("\n", '')
    full_text = data["3"]["full_text"].replace("\n", '')
    print(get_keywords(summary, full_text))
