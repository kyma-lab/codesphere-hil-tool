import numpy as np
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

DOMAIN_THESAURUS = ""  # TODO: Add Domain Thesaurus directory, change to json File containing domain Thesaurus data
VEC_DIRECTORY = "./vectorized_norms.json"
ELASTIC_HOST = "https://elastic.simplex.fmi.uni-jena.de"

es = None
not_connected = True


try:
    es = Elasticsearch(ELASTIC_HOST)
    es.info()
    not_connected = False
except Exception as e:
    print("Could not connect to Elasticsearch.")
    print(e)

def umlauts(text):
    """
    Replaces German umlauts and ß with their respective ASCII representations.

    Args:
        text (str): Input text.

    Returns:
        tempVar (str): Text with replaced umlauts.
    """
    tempVar = text
    tempVar = tempVar.replace("ä", "ae")
    tempVar = tempVar.replace("ö", "oe")
    tempVar = tempVar.replace("ü", "ue")
    tempVar = tempVar.replace("Ä", "Ae")
    tempVar = tempVar.replace("Ö", "Oe")
    tempVar = tempVar.replace("Ü", "Ue")
    tempVar = tempVar.replace("ß", "ss")
    return tempVar


def get_mean_vector(word2vec_model, words):
    """
    Calculates the mean vector of a list of words using a word2vec model.

    Args:
        word2vec_model: Word2Vec model.
        words (list): List of words.

    Returns:
        mean_vector (numpy.ndarray): Mean vector of the words.
    """
    # remove out-of-vocabulary words
    words = [word for word in words if word in word2vec_model.wv.key_to_index]
    if len(words) >= 1:
        return np.mean(word2vec_model.wv[words], axis=0)
    else:
        return []


def calculateEmbeddingBert(query):
    """
    Calculates the embedding vector of a query using a pre-trained BERT model.

    Args:
        query (str): Input query.

    Returns:
        vector (list): Embedding vector of the query.
    """
    query = umlauts(query)

    # https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v1

    model = SentenceTransformer(
        "./shared/base-models/distiluse-base-multilingual-cased-v1"
    )
    vector = model.encode(query)
    vector = vector.tolist()
    return vector
