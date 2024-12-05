import json

from handlers.database.esearch import submitQueryTFIDF, submitQueryBERT

# todo: make this configurable via config file
DISABLE_SEMANTIC_SEARCH = False

def handle_semantic_search(logger, query):
    """ 
        Performs a semantic search with the given query.
        Requires that the Elastic / Kibana server is reachable and set up correctly.
    """
    
    if DISABLE_SEMANTIC_SEARCH:
        return "Semantic search is disabled", 400, []

    if not query:
        logger.debug("returned 400, query parameter is required.")
        return "Query parameter is required", 400, []
    
    results = submitQueryBERT(query)

    try:
        logger.debug("parsing search results")
        results_list = [
            {
                "id": hit["_id"],
                "jurabk": hit["_source"]["jurabk"],
                "link": hit["_source"]["link"],
                "enbez": hit["_source"]["enbez"],
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
            }
            for hit in results["hits"]["hits"]
        ]
        return "success", 200, results_list

    except Exception as e:
        logger.error(e)
        return "An error occurred while processing the search results", 500, []


def handle_search(logger, query):
    """ 
        Performs a regular (text-based) search with the given query.
        Requires that the Elastic / Kibana server is reachable and set up correctly.
    """
    
    
    if not query:
        logger.debug("returned 400, query parameter is required.")
        return "Query parameter is required", 400, []

    results = submitQueryTFIDF(query)

    try:
        logger.debug("parsing search results")
        results_list = [
            {
                "id": hit["_id"],
                "jurabk": hit["_source"]["jurabk"],
                "link": hit["_source"]["link"],
                "enbez": hit["_source"]["enbez"],
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
            }
            for hit in results["hits"]["hits"]
        ]

        return "success", 200, results_list
    except Exception as e:
        logger.error(e)
        return "An error occurred while processing the search results", 500, []
