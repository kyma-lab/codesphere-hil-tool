from elasticsearch import Elasticsearch, helpers
import json
import ast

from .querymodification import *


# this is a tool for creating the index in elasticsearch
# functions of this are used by the server


# Directory of vectorized laws, only required for initial indexing
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


# not used in server, only for initial index creation
def index_documents_bulk():
    with open(VEC_DIRECTORY) as vec_file:
        vecdata = json.load(vec_file)
        counter = 0
        actions = []
        for doc in vecdata["norms"]:  # create action object for bulk upload
            action = {
                "_index": "laws_vectors",
                "_op_type": "index",
                "_id": counter,
                "_source": doc,
            }
            counter = counter + 1
            actions.append(action)
        res = helpers.bulk(es, actions)


# used in submitQueryBERT
def send_query_cosine(vector, law_index):
    search_param = {
        "_source": ["jurabk", "enbez", "title", "content", "link"],
        "size": 10,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.queryVector, 'vector') + 1.0",
                    "params": {"queryVector": vector},
                },
            }
        },
    }
    # Perform the search
    res = es.search(index=law_index, body=search_param, request_timeout=30)
    # Convert the response to a Python dictionary
    res = ast.literal_eval(str(res))
    return res


def submitQueryTFIDF(query):

    if not_connected:
        print("es error, not connected")
        return {"error": "Elasticsearch connection error"}

    search_param = {
        "_source": ["jurabk", "enbez", "title", "content", "link"],
        "size": 10,
        "query": {"query_string": {"query": query, "default_field": "content"}},
    }
    # Perform the search
    # TODO: Add index name from elasticsearch
    res = es.search(index="laws_no_vectors", body=search_param)
    # Convert the response to a Python dictionary
    res = ast.literal_eval(str(res))
    return res


def submitQueryBERT(query):

    if not_connected:
        print("es error, not connected")
        return {"error": "Elasticsearch connection error"}

    law_index = "laws_vectors"  # TODO: Add index name from elasticsearch
    vector = calculateEmbeddingBert(query)
    print(vector)
    res = send_query_cosine(vector, law_index)
    return res
