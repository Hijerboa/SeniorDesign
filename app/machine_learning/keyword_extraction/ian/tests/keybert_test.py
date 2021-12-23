from utility import *
from keybert import KeyBERT

stopwords = ['' ,'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than']
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
stopwords = []

def remove_stopwords(in_string):
    out_string = ""
    split_string = in_string.split(' ')
    for word in split_string:
        if word not in stopwords:
            out_string += word + " "
    return out_string


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
    

doc = "Efficient Use of Government Spectrum Act of 2013 - Directs the Federal Communications Commission (FCC), within three years after enactment of the Middle Class Tax Relief and Job Creation Act of 2012, to: (1) reallocate electromagnetic spectrum between the frequencies from 1755 to 1780 megahertz (currently, such frequencies are occupied by the Department of Defense [DOD] and other federal agencies); and (2) as part of the competitive bidding auctions required by such Act, grant new initial licenses, subject to flexible-use service rules, for the use of such spectrum, paired with the spectrum between frequencies from 2155 to 2180 megahertz already designated for auction. Directs the proceeds attributable to the competitive bidding of the 1755 to 1780 megahertz range to be allocated in the same manner as other specified frequencies pursuant to such Act for uses including reimbursements to agencies for relocation and sharing costs, the building of the nationwide public safety broadband network, and deposits or reimbursements to the U.S. Treasury.  Requires such spectrum to be relocated in a manner to ensure cooperation between federal and commercial entities under procedures in the National Telecommunications and  Information Administration Organization Act, except for DOD-operated spectrum, which shall be relocated under the National Defense Authorization Act for Fiscal Year 2000.  Directs federal entities operating a federal government station, within a specified period before  commencement of competitive bidding, to identify stations that cannot be relocated without jeopardizing essential military capability. Requires the transition plans of federal entities identifying such essential spectrum to: (1) provide for non-federal users to share such stations, and (2) limit any necessary exclusion zones to the smallest possible zones. Directs the President to withdraw assignments upon relocation or to modify assignments to permit federal and non-federal use."

def keybert_test1():
    global doc
    doc = remove_stopwords(doc)

    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 3), stop_words=None, top_n=10)

    return keywords


def keybert_extraction(summary: str, full_text: str):
    kw_model = KeyBERT()

    n_gram_range = (2, 4)
    stop_words = None # 'english'
    top_n = 10
    # MMR (Maximal Marginal Relevance) | if set to true, diversity specifies how related the keywords are
    # For example, diversity of 0.8 may result in lower confidence but much more diverse words
    use_mmr = True
    diversity = 0.3
    
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

if __name__ == "__main__":
    bill_num = "3"

    bill_data = "/Users/ianwu/Desktop/Senior Design/SeniorDesign/app/machine_learning/keyword_extraction/ian/tests/Sample_Bill_Data.txt"
    data = load_json_from_file(bill_data)
    summary = data[bill_num]["summary"].replace("\n", '')
    summary = remove_stopwords(summary)
    full_text = data[bill_num]["full_text"].replace("\n", '')
    full_text = remove_stopwords(full_text)

    keybert_extraction(summary, full_text)
