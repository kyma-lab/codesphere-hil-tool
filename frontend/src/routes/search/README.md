# Semantic Search System for German Legal Norms

This system enables users to search over German legal norm documents. Legal documents are downloaded from "Gesetze-im-Internet.de" via the "Rechtsinformationsportal" API. Furthermore, the search is aided by word and document embeddings, and query expansion techniques (pseudo Relevance Feedback and Thesaurus based expansion).

**Features:**

- Pre-processing and indexing of documents to Elastic Search
- Simple Okapi BM25 ranking based search
- Doc2vec ranking based search
- Word2vec ranking based search
- SBERT ranking based search
- pseudo Relevance Feedback based query expansion (with changeable size of expansion)
- General (openthesaurus.de, GermaNet) and domain specific (Wolters Kluwer German labour law) Thesaurus based expansion (with changeable size of expansion)


**Installation:**

Elastic Search Python API:
    ```$ python -m pip install elasticsearch```

Requests for using APIs:
    ```$ python -m pip install requests```

Pre-processing html to text (removes html from our data):
    ```$ pip install html2text```

Pandas Dataframes (used for embedding models):
    ```$ pip install pandas```

Gensim (for doc2vec related code):
    ```$ pip install --upgrade gensim```

Numpy (used to find mean vector):
    ```$ pip install numpy```

NLTK:
    ```$ pip install nltk```

HanTa lemmatizer:
    ```$ pip install hanta```

Sentence Transformers (SBERT):
    ```$ pip install -U sentence-transformers```

When working with GermaNet thesaurus:
    ```$ pip install germanetpy```

Svelte:
    - navigate to directory and use ```npm run dev``` to start the Svelte App

FastAPI:
    - navigate to directory and use ```uvicorn frontendbackendapi:app --reload``` to start FastAPI

**How to use:**

- esearch.py:
    - to index documents
    - to send queries to Elastic Search

- getdocuments.py:
    - to bulk download laws
    - to download the domain specific Thesaurus

- preprocessing.py:
    - to pre-process of documents

- wordembedding.py:
    - to train doc2vec and append vectors to JSON
    - to train word2vec and append vectors to JSON
    - to train SBERT and append vectors to JSON
    
- querymodification.py:
    - to expand a query using pseudo Relevance Feedback
    - to expand a query using a general Thesaurus
    - to expand a query using a domain specific Thesaurus
    - for word-sense-disambiguation using embedding models
    - to calculate embeddings for a query

# UPDATE

> new readme from friedrich

tool_crawler.py:

- finds links of laws under https://www.gesetze-im-internet.de/gii-toc.xml
- for each law, finds the respective norms
- stores norms in json format

wordembedding.py:

- generates vectors for norms based on sentence-transformers/distiluse-base-multilingual-cased-v1
- appends vectors to json documents

esearch.py:

- indexes json documents in bulk to elastic search instance
- TFIDF text based search
- cosine similarity based semantic search (ranking of similar query and document vectors)

Semantic Search:
- when a query is entered, a vector representing the query is calculated using sentence-transformers/distiluse-base-multilingual-cased-v1
- that vector is compared to all the documents' vectors from the collection (the vectors for the documents were generated using the same model) through cosine similarity
- the 10 documents that are the most similar to the query vector are presented to the user as the result

Text-based Search:
- The submitted query is used to search the document corpus using Okapi BM25 (TF-IDF variant)
- the 10 documents that ranked highest are presented to the user