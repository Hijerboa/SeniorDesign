from keybert import KeyBERT

stopwords = {'' ,'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'} 

def remove_stopwords(in_string):
    out_string = ""
    split_string = in_string.split(' ')
    for word in split_string:
        if word not in stopwords:
            out_string += word + " "
    return out_string

doc = "Efficient Use of Government Spectrum Act of 2013 - Directs the Federal Communications Commission (FCC), within three years after enactment of the Middle Class Tax Relief and Job Creation Act of 2012, to: (1) reallocate electromagnetic spectrum between the frequencies from 1755 to 1780 megahertz (currently, such frequencies are occupied by the Department of Defense [DOD] and other federal agencies); and (2) as part of the competitive bidding auctions required by such Act, grant new initial licenses, subject to flexible-use service rules, for the use of such spectrum, paired with the spectrum between frequencies from 2155 to 2180 megahertz already designated for auction. Directs the proceeds attributable to the competitive bidding of the 1755 to 1780 megahertz range to be allocated in the same manner as other specified frequencies pursuant to such Act for uses including reimbursements to agencies for relocation and sharing costs, the building of the nationwide public safety broadband network, and deposits or reimbursements to the U.S. Treasury.  Requires such spectrum to be relocated in a manner to ensure cooperation between federal and commercial entities under procedures in the National Telecommunications and  Information Administration Organization Act, except for DOD-operated spectrum, which shall be relocated under the National Defense Authorization Act for Fiscal Year 2000.  Directs federal entities operating a federal government station, within a specified period before  commencement of competitive bidding, to identify stations that cannot be relocated without jeopardizing essential military capability. Requires the transition plans of federal entities identifying such essential spectrum to: (1) provide for non-federal users to share such stations, and (2) limit any necessary exclusion zones to the smallest possible zones. Directs the President to withdraw assignments upon relocation or to modify assignments to permit federal and non-federal use."
doc = remove_stopwords(doc)

kw_model = KeyBERT()
keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 3), stop_words=None, top_n=10)

print(keywords)