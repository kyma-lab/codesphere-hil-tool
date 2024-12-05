# Semantic Search System for German Legal Norms

This system enables users to search over German legal norm documents. It provides a text-based and a semantic search over German laws. Semantic search extends purely text based search by trying to understand the underlying meaning of a query. In this prototype, this is accomplished by the use of document embedding. Legal documents are downloaded from "Gesetze-im-Internet.de". To store and search over the laws, we chose to work with the document based Database Elasticsearch.
 
 ![Search Architecture](./graphics/SemanticSearch.jpg)

**Features**

- "Gesetze-Im-Internet"-Crawler for downloading latest Laws
- Pre-processing and indexing of documents to Elastic Search
- Simple Okapi BM25 ranking based search
- SBERT ranking based Semantic Search


**Installation**

Elastic Search Python API:
    ```$ python -m pip install elasticsearch```


Sentence Transformers (SBERT):
    ```$ pip install -U sentence-transformers```

**Details**

***"Gesetze-Im-Internet" - Crawler:***

The Crawler finds all current law articles from "Gesetze-Im-Internet".

- It finds all the current norms and filters the relevant fields for our search case:
    - Abbreviation ("jurabk")
    - Title ("titel")
    - Narrow Title ("engbez")
    - Content of the Norm
    - Link to the Norm
- All the information found is appended to a single JSON file.

***Document Embeddings (wordembeddings.py):***

This calcualtes the embeddings for the laws that are retrieved from the "Gesetze-Im-Internet" Crawler.

- For each law, we encode the "content" field using the Sentence Transformer model distiluse-base-multilingual-cased-v1.
- The vector is appended to the JSON document.

***Elastic Search (esearch.py):***

Used for the connection to our Elasticsearch instance via its Python API

Two main functions:
- Indexing/Uploading law documents to Elasticsearch
- Sending Queries to Elasticsearch and receiving results

Indexing of Laws:
- Indexing of laws is done in bulk
- The law documents are stored in one JSON file
- In the case of our semantic search, there is an extra JSON field that contains the vector embeddings of the document
- In the case of our text based search, no such field is necessary.
- The Index has to be created beforehand and a mapping needs to be defined for the documents containing embeddings (for the next step)

Sending Queries and Retrieval of Results:

Text-based Search:
- In the case of the text based search, the appropriate Index is referred to and the Query is used "as-is", meaning it is not altered in any way.
- For this default search function, Elasticsearch uses the Okapi BM-25 Ranking-Algorithm, which is a TF-IDF variant.

Semantic-Search:
- In the case of our Semantic Search, in a first step, the embedding for the Query are calculated using the same model used in the calculation of the document embeddings (The Sentence Transformer model distiluse-base-multilingual-cased-v1)
- Then, Elasticsearch calcualtes the cosine-similarity of the query vector to the document vectors and ranks them.

Retrieval of Results:
- In both cases, we retrieve the then highest ranking law documents
- The documents are provided in JSON format

***Frontend and Backend API:***
Provides the connection to the frontend:
- Search requests are forwarded to the esearch.py module.
- Retrieved results are forwarded to the Frontend.
