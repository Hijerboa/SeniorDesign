# imports
import yake
import spacy
from rake_nltk import Rake
from gensim.summarization import keywords
from utility import *

bill_data = "Sample_Bill_Data.txt"


# Wordcount seems to have some use but we would need 
# to filter out some of the most used words that are
# generic or irrelevant
def wordcount_exploration(string):
    print(get_word_counts(string))


# YAKE: yet another keyword extractor
# Takes a statistical approach to keyword extraction
# Works pretty good, high level of customizability (e.g. n-gram specification)
# Some filtering would still be good
def yake_exploration(string):
    custom_kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=20, features=None)
    keywords = custom_kw_extractor.extract_keywords(string)

    for word in keywords:
        print(word)


# spacy
# need to run "python3 -m spacy download en_core_web_lg" to get model
# can get smaller models using "en_core_web_md" and "en_core_web_sm"
# Not bad, still gets too many keywords
def spacy_exploration(string):
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(string)
    print(doc.ents)


# NON-FUNCTIONAL CURRENTLY
# RAKE: Rapid Automatic Keyword Extraction
# uses nltk stopwords and cannot download
def rake_exploration(string):
    rake_nltk_var = Rake()

    rake_nltk_var.extract_keywords_from_text(string)
    keyword_extracted = rake_nltk_var.get_ranked_phrases()

    print(keyword_extracted)


# Gensim
# Way too broad
# maybe useful for filtering keywords in other methods?
def gensim_exploration(string):
    print(keywords(string))


# Graph based approach to find keywords? (Textrank?)

# Can find keywords with BERT. A lot of work :(

# list of keywords to exclude - WIP
bad_keywords = ["united states", "act", "section", "united", "states", "united states of america", "secretary", "federal", "federal government", "government", "congressional", "congress", "bill", "bills", "congress", "senate", "america", "state", "agency", "federal agency", "military", "spending", "healthcare"]

def cleanup(my_list: list):
    # remove confidence scores
    my_list = list(map(lambda x: x[0], my_list))

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


def yake_extraction(summary: str, full_text: str):
    # YAKE keyword extraction parameters
    language = "en"
    max_ngram_size = 3
    deduplication_thresold = 0.25
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 20
    
    # get keywords
    extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
    keywords = extractor.extract_keywords(summary + " " + full_text)

    return cleanup(keywords)

if __name__ == "__main__":
    bill_num = "2"

    bill_data = "/Users/ianwu/Desktop/Senior Design/SeniorDesign/app/machine_learning/keyword_extraction/ian/tests/Sample_Bill_Data.txt"
    data = load_json_from_file(bill_data)
    summary = data[bill_num]["summary"].replace("\n", '')
    full_text = data[bill_num]["full_text"].replace("\n", '')
    # string = remove_stopwords(string)

    words = yake_extraction(summary, full_text)

    for i in words:
        print(i)
