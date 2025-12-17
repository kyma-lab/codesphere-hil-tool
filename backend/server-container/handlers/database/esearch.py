from elasticsearch import Elasticsearch, helpers
import json
import ast

from querymodification import calculateEmbeddingBert

# Configuration
ELASTIC_HOST = "https://elastic.simplex.fmi.uni-jena.de"
NO_VEC_DIRECTORY = "norms_only.json"
VEC_DIRECTORY = "vectorized_norms.json"

# Elasticsearch connection
try:
    es = Elasticsearch(ELASTIC_HOST)
    es.info()
    print("Connected to Elasticsearch.")
except Exception as e:
    es = None
    print("Could not connect to Elasticsearch:", e)


def delete_index(index_name: str):
    """Delete an existing Elasticsearch index."""
    if es and es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted.")
    else:
        print(f"Index '{index_name}' does not exist or ES not connected.")


def create_index(index_name: str, mapping: dict):
    """Create an Elasticsearch index with the provided mapping."""
    if es:
        try:
            es.indices.create(index=index_name, body=mapping)
            print(f"Index '{index_name}' created.")
        except Exception as e:
            print(f"Index creation failed for '{index_name}':", e)


def create_laws_no_vectors_index():
    mapping = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 1},
        "mappings": {
            "properties": {
                "jurabk": {"type": "keyword"},
                "enbez": {"type": "text", "analyzer": "standard"},
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "standard"},
                "link": {"type": "keyword"},
            }
        },
    }
    create_index("laws_no_vectors", mapping)


def create_laws_vectors_index():
    mapping = {
        "mappings": {
            "properties": {
                "jurabk": {"type": "keyword"},
                "enbez": {"type": "text"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "link": {"type": "keyword"},
                "vector": {"type": "dense_vector", "dims": 512, "index": True, "similarity": "cosine"},
            }
        }
    }
    create_index("laws_vectors", mapping)


def index_documents_bulk(file_path: str, index_name: str):
    """Bulk index documents from a JSON file."""
    if not es:
        print("Elasticsearch not connected.")
        return

    try:
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        print("Failed to load JSON:", e)
        return

    actions = [
        {
            "_index": index_name,
            "_id": i,
            "_source": doc
        }
        for i, doc in enumerate(data.get("norms", []))
    ]

    try:
        success, errors = helpers.bulk(es, actions, raise_on_error=False)
        print(f"Bulk indexed {success} documents into '{index_name}'.")
        if errors:
            print("Sample errors:", errors[:3])
    except Exception as e:
        print("Bulk indexing failed:", e)


def send_query_cosine(vector, index_name, size=10):
    """Search a vector index using cosine similarity."""
    if not es:
        return {"error": "Elasticsearch not connected"}

    search_body = {
        "_source": ["jurabk", "enbez", "title", "content", "link"],
        "size": size,
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
    res = es.search(index=index_name, body=search_body, request_timeout=30)
    return ast.literal_eval(str(res))


def submit_query_tfidf(query, index_name="laws_no_vectors"):
    """Submit a TF-IDF search query."""
    if not es:
        return {"error": "Elasticsearch not connected"}

    search_body = {
        "_source": ["jurabk", "enbez", "title", "content", "link"],
        "size": 10,
        "query": {"query_string": {"query": query, "default_field": "content"}},
    }
    res = es.search(index=index_name, body=search_body)
    return ast.literal_eval(str(res))


def submit_query_bert(query, index_name="laws_vectors"):
    """Submit a semantic search query using BERT embeddings."""
    if not es:
        return {"error": "Elasticsearch not connected"}

    vector = calculateEmbeddingBert(query)
    return send_query_cosine(vector, index_name)


if __name__ == "__main__":
    # Example usage
    delete_index("laws_no_vectors")
    delete_index("laws_vectors")
    create_laws_no_vectors_index()
    create_laws_vectors_index()
    index_documents_bulk(NO_VEC_DIRECTORY, "laws_no_vectors")
    index_documents_bulk(VEC_DIRECTORY, "laws_vectors")
