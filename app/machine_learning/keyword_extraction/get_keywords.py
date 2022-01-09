# imports
from functools import reduce
from numpy.core.numeric import full
import yake
from keybert import KeyBERT

# list of keywords to exclude - WIP
bad_keywords = ["united states", "act", "section", "united", "states", "united states of america", "secretary", "federal", "federal government", "government", "congressional", "congress", "bill", "bills", "congress", "senate", "america", "state", "agency", "federal agency", "military", "spending", "healthcare"]
stopwords = ['', 'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']


# YAKE keyword extraction parameters
language = "en"
max_ngram_size = 3
deduplication_thresold = 0.45
deduplication_algo = 'seqm'
windowSize = 3
numOfKeywords = 20

extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)

kw_model = KeyBERT()

def remove_stopwords(in_string):
    out_string = ""
    split_string = in_string.split(' ')
    for word in split_string:
        if word not in stopwords:
            out_string += word + " "
    return out_string


def cleanup(my_list: list):
    # remove confidence scores
    my_list = list(map(lambda x: x[0], my_list))

    # remove any monograms
    my_list = filter(lambda x: len(x.split(" ")) > 1, my_list)
    
    # remove unuseful keywords
    my_list = [word for word in my_list if word not in bad_keywords]

    # remove stopwords from selected keywords/phrases
    my_list = list(map(lambda x: remove_stopwords(x), my_list))

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

    n_gram_range = (2, 4)
    stop_words = None # 'english'
    top_n = 10
    # MMR (Maximal Marginal Relevance) | if set to true, diversity specifies how related the keywords are
    # For example, diversity of 0.8 may result in lower confidence but much more diverse words
    use_mmr = True
    summary_diversity = 0.3
    fulltext_diversity = 0.4
    
    summary_keywords = kw_model.extract_keywords(
        docs=summary, 
        keyphrase_ngram_range=n_gram_range, 
        stop_words=stop_words, 
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=summary_diversity)

    # For keyBERT, we do 1 - x[1] in the sort method since highest confidence value is best
    keywords = summary_keywords
    keywords.sort(key = lambda x: 1 - x[1])
    keywords = remove_dups(keywords)
    
    return cleanup(keywords)


def get_keywords(summary: str):
    summary = summary.lower()

    yake_keywords = yake_extraction(summary)
    keybert_keywords = keybert_extraction(summary)

    return list(set(yake_keywords + keybert_keywords))


# TESTING
import json
if __name__ == "__main__":
    data = json.load(open("/home/nicleary/Documents/Repos/SeniorDesign/app/machine_learning/keyword_extraction/ian/tests/Sample_Bill_Data.txt"), strict=False)

    for i in [1, 3]:
        summary = data[f"{i}"]["summary"].replace("\n", '')
        full_text = data[f"{i}"]["full_text"].replace("\n", '')
        print(f'Bill #{i}\n---------------\n')
        for word in test_get_keywords(summary, full_text):
            print(f"          {word}")

# SHOULD INCLUDE BILL TITLE AS KEYWORD
