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


if __name__ == "__main__":
    data = load_json_from_file(bill_data)
    string = data["3"]["full_text"].replace("\n", '')
    string = remove_stopwords(string)

    spacy_exploration(string)