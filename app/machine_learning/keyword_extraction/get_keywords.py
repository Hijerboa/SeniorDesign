# imports
from functools import reduce
from string import punctuation
from numpy.core.numeric import full
import yake
from keybert import KeyBERT
from db.models import Bill, BillVersion

# Prefixes for title-based keywords
prefixes = {
    "hr" : ["HB ", "HB-", "H.B. ", "House Bill ", "H Bill "],
    "hres" : ["hres ", "House Res ", "House Resolution ", "H Res ", "HR ", "H.R. ", ],
    "hconres" : ["hconres ", "House Concurrent Res ", "House Con Res ", "House ConRes ", "House Concurrent Resolution ", "House Con Resolution ", "H Con Res ", "H Concurrent Res ", "H Concurrent Resolution ", "H Con Resolution ", "HR Con Res ", "HR Concurrent Res ", "HR Concurrent Resolution ", "HR Con Resolution ", "H.C.R. ", ],
    "hjres" : ["hjres ", "House Joint Res ", "House Joint Resolution ", "H J Res ", "H Joint Res ", "H J Res ", "HR J Res ", "HR Joint Res ", "HR J Res ", "HJR ", "H.J.R. ", ],
    "s" : ["SB ", "SB-", "S.B. ", "Senate Bill ", "S Bill "],
    "sres" : ["sres ", "Senate Res ", "Senate Resolution ", "S Res ", "S Resolution ", "SR ", "S.R. ", ],
    "sconres" : ["sconres ", "Senate Concurrent Res ", "Senate Con Res ", "Senate ConRes ", "Senate Concurrent Resolution ", "Senate Con Resolution ", "S Con Res ", "S Concurrent Res ", "S Concurrent Resolution ", "S Con Resolution ",  "S.C.R. ", ],
    "sjres" : ["sjres ", "Senate Joint Res ", "Senate Joint Resolution ", "S J Res ", "S Joint Res ", "S Joint Resolution ", "S J Resolution ", "SJR ", "S.J.R. ", ],
}

# list of keywords to exclude
bad_keywords = ["united states", "act", "section", "united", "states", "united states of america", "secretary", "federal", "federal government", "government", "congressional", "congress", "bill", "bills", "congress", "senate", "america", "state", "agency", "federal agency", "military", "spending", "healthcare", "prohibits federal", "good conscience"]
stopwords = ['', 'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

# YAKE extractor object
language = "en"
max_ngram_size = 3
deduplication_thresold = 0.45
deduplication_algo = 'seqm'
windowSize = 3
numOfKeywords = 20
extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

# KeyBERT keyword extraction model object
n_gram_range = (2, 4)
stop_words = None # 'english'
top_n = 10
# MMR (Maximal Marginal Relevance) | if set to true, diversity specifies how related the keywords are
# For example, diversity of 0.8 may result in lower confidence but much more diverse words
use_mmr = True
kb_diversity = 0.4
kw_model = KeyBERT()


def get_base_keywords(bill: Bill):
    if bill.bill_type not in prefixes.keys():
        return []

    prefix_list = prefixes[bill.bill_type]
    number = bill.number.split(".")[-1]

    return [bill.bill_id, bill.number] + list(map(lambda x: x + number, prefix_list))


def remove_stopwords(in_string):
    out_string = ""
    split_string = in_string.split(' ')
    for word in split_string:
        if word not in stopwords:
            out_string += word + " "
    return out_string[:-1]


def remove_punc(in_string):
    out_string = in_string
    for punc_mark in punctuation:
        out_string = in_string.replace(punc_mark, "")
    return out_string


def cleanup(my_list: list):
    # remove confidence scores
    my_list = list(map(lambda x: x[0], my_list))

    # remove stopwords from selected keywords/phrases
    my_list = list(map(lambda x: remove_stopwords(x), my_list))

    # remove punctuation from keywords
    my_list = list(map(lambda x: remove_punc(x), my_list))

    # remove any monograms
    my_list = filter(lambda x: len(x.split(" ")) > 1, my_list)
    
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


def yake_extraction(summary: str):
    keywords = extractor.extract_keywords(summary)

    return cleanup(keywords)


def keybert_extraction(summary: str):
    
    
    summary_keywords = kw_model.extract_keywords(
        docs=summary, 
        keyphrase_ngram_range=n_gram_range, 
        stop_words=stop_words, 
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=kb_diversity)

    # For keyBERT, we do 1 - x[1] in the sort method since highest confidence value is best
    keywords = summary_keywords
    keywords.sort(key = lambda x: 1 - x[1])
    keywords = remove_dups(keywords)
    
    return cleanup(keywords)


def derive_keywords(summary: str):
    summary = summary.lower()

    yake_keywords = yake_extraction(summary)
    keybert_keywords = keybert_extraction(summary)
    
    return list(set(yake_keywords + keybert_keywords))


def get_keywords(bill: Bill):
    # get list of obvious keywords
    known_keywords = get_base_keywords(bill)
    # use NLP to generate other keywords
    generated_keywords = derive_keywords(bill.summary.replace('\n', ''))
    
    return list(set(known_keywords + generated_keywords))
