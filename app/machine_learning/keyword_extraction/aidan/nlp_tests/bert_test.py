from common import get_text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT

text = get_text()

kw_model = KeyBERT()
n_gram_range = (1, 3)
keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=n_gram_range, stop_words = None, top_n=15)
for keyword in keywords:
    print(f'{keyword[1]} | {keyword[0]}')

def manual_way():
    # 1. Get Candidate keywords / phrases
    n_gram_range = (1, 3)
    stop_words = 'english'
    count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([text])
    candidates = count.get_feature_names()

    #2. Convert the original text and candidates into embeddings
    # This model is recommended from article
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    doc_embedding = model.encode([text])
    candidate_embeddings = model.encode(candidates)

    #3. Cosine Similarity
    top_n = 15
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
    for keyword in keywords:
        print(keyword)