# imports
from keybert import KeyBERT
from db.models import Bill, BillVersion
import nltk
from nltk.stem import WordNetLemmatizer

# Prefixes for title-based keywords
prefixes = {
    "hr": ["HB ", "HB-", "H.B. ", "House Bill ", "H Bill "],
    "hres": ["hres ", "House Res ", "House Resolution ", "H Res ", "HR ", "H.R. ", ],
    "hconres": ["hconres ", "House Concurrent Res ", "House Con Res ", "House ConRes ", "House Concurrent Resolution ", "House Con Resolution ", "H Con Res ", "H Concurrent Res ", "H Concurrent Resolution ", "H Con Resolution ", "HR Con Res ", "HR Concurrent Res ", "HR Concurrent Resolution ", "HR Con Resolution ", "H.C.R. ", ],
    "hjres": ["hjres ", "House Joint Res ", "House Joint Resolution ", "H J Res ", "H Joint Res ", "H J Res ", "HR J Res ", "HR Joint Res ", "HR J Res ", "HJR ", "H.J.R. ", ],
    "s": ["SB ", "SB-", "S.B. ", "Senate Bill ", "S Bill "],
    "sres": ["sres ", "Senate Res ", "Senate Resolution ", "S Res ", "S Resolution ", "SR ", "S.R. ", ],
    "sconres": ["sconres ", "Senate Concurrent Res ", "Senate Con Res ", "Senate ConRes ", "Senate Concurrent Resolution ", "Senate Con Resolution ", "S Con Res ", "S Concurrent Res ", "S Concurrent Resolution ", "S Con Resolution ",  "S.C.R. ", ],
    "sjres": ["sjres ", "Senate Joint Res ", "Senate Joint Resolution ", "S J Res ", "S Joint Res ", "S Joint Resolution ", "S J Resolution ", "SJR ", "S.J.R. ", ],
}

# list of keywords to exclude
nono_words = set(["denies", "establishes", "reauthorizes", "regard", "applicable","shall", "nullifies", "whereas", "representatives", "con", "res", "increases", "considering", "amended", "resolution", "commends", "proposes", "continuing", "directs", "regarding", "eliminates", "exempting", "amends", "requires", "united states", "act", "section", "united", "states", "united states of america", "secretary", "federal", "federal government", "government", "congressional", "congress", "bill", "bills", "congress", "america", "state", "agency", "federal agency", "prohibits federal", "good conscience"])
stopwords = set(['', 'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'])

# KeyBERT keyword extraction model object
n_gram_range = (2, 4)
stop_words = stopwords # 'english'
top_n = 5
# MMR (Maximal Marginal Relevance) | if set to true, diversity specifies how related the keywords are
# For example, diversity of 0.8 may result in lower confidence but much more diverse words
use_mmr = True
kb_diversity = 0.3
kw_model = KeyBERT()
nltk.download('wordnet')
nltk.download('omw-1.4')

def get_base_keywords(bill: Bill):
    if bill.bill_type not in prefixes.keys():
        return []

    prefix_list = prefixes[bill.bill_type]
    number = bill.number.split(".")[-1]

    return [bill.bill_id, bill.number] + list(map(lambda x: x + number, prefix_list))


def kw_cleanup(text):
    # Remove Punctuation (Unneeded)
    # text = remove_punc(text)
    # Tokenize
    tokens = text.split(" ")
    # Remove Stopwords
    tokens = [tok for tok in tokens if tok not in stop_words]
    # Stem
    ls = WordNetLemmatizer()
    tokens = [ls.lemmatize(tok) for tok in tokens]
    # Remove bad words
    tokens = [tok for tok in tokens if tok not in nono_words]
    return ' '.join(tokens)

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
    
    return keywords


def derive_keywords(summary: str):
    summary = summary.lower()
    summary = kw_cleanup(summary)

    keybert_keywords = keybert_extraction(summary)
    
    return list(set(keybert_keywords))


def get_keywords(bill: Bill):
    # get list of obvious keywords
    known_keywords = get_base_keywords(bill)
    # use NLP to generate other keywords
    if (bill.summary is None or len(bill.summary) > 100000) and bill.summary_short is not None:
        generated_keywords = derive_keywords(bill.summary_short.replace('\n', ''))
    elif bill.summary_short is not None and len(bill.summary) < 100000:
        generated_keywords = derive_keywords(bill.summary.replace('\n', ''))
    else:
        generated_keywords = []
    return [word[0] for word in generated_keywords], known_keywords