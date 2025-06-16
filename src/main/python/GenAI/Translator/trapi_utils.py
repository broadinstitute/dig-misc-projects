
# imports
import requests
import json
import constants_utils as cutils


# constants
URL_TRANSLATOR_QUERY = "{}/query"

URL_NAME_RESOLVER ="https://name-lookup.transltr.io/lookup?limit={}&string={}"


# methods
def query_trapi_rest_service(endpoint_url, list_target, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], log=False):
    """
    Sends a POST request to a REST service with the given list of source IDs.

    Parameters:
    - source_ids (list of str): The list of source IDs to include in the payload.
    - endpoint_url (str): The URL of the REST service.

    Returns:
    - dict: The JSON response from the REST service.
    """
    response = {}
    result = {}

    # do the call
    try:
        payload = {
            "message": {
                "query_graph": {
                    "nodes": {
                        "source": {
                            "categories": list_source_types
                        },
                        "target": {
                            "ids": list_target,
                            "categories": list_target_types
                        }
                    },
                    "edges": {
                        "e03": {
                            "subject": "source",
                            "object": "target",
                            "predicates": list_predicates 
                        }
                    }
                }
            }
        }

        if log:
            print("sending payload: \n{}".format(json.dumps(payload, indent=2)))

        headers = {"Content-Type": "application/json"}

        # make REST call
        response = requests.post(URL_TRANSLATOR_QUERY.format(endpoint_url), headers=headers, data=json.dumps(payload))
        # print("got response: {}".format(response))
        result = response.json()

        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
    except Exception as e:
        print(f"An general error occurred: {e}")

    # return
    return result


def get_curies(entity_name, list_ontologies, limit=5, log=False):
    '''
    gets the ontology ids for an input
    '''
    list_result = []
    url = URL_NAME_RESOLVER.format(limit, entity_name)

    # do the call
    try:
        response = requests.post(url, json={}, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        map_json = response.json()

        if log:
            print("got json result: {}".format(json.dumps(map_json, indent=2)))

        list_result = [s.get('curie', "") for s in map_json if any(sub in s.get('curie', "") for sub in list_ontologies)]

        # return response.json()       # Returns the parsed JSON content

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")

    # log
    if log:
        print("return curie list: {}".format(list_result))

    # return
    return list_result


def query_trapi_for_string(endpoint_url, entity_name, list_ontologies, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], 
                           sort=True, descending=False, field_to_sort=None, log=False):
    '''
    query name resolver first for curies, then the service itself an translate
    '''
    # initialize
    map_trapi_response = {}
    list_result = []
    list_curies = []

    # get the list of curies
    list_curies = get_curies(entity_name=entity_name, list_ontologies=list_ontologies, log=log)

    if len(list_curies) > 0:
        # log
        if log:
            print("querying endpoint: {}".format(endpoint_url))

        # do the trapi query
        map_trapi_response = query_trapi_rest_service(endpoint_url=endpoint_url, list_target=list_curies, list_predicates=list_predicates, 
                                                    list_source_types=list_source_types, list_target_types=list_target_types, log=log)
        
        # log
        if log:
            print("translating trapi result: \n{}".format(json.dumps(map_trapi_response, indent=2)))
        
        # translate
        list_result = translate_trapi_results(map_trapi=map_trapi_response, sort=sort, descending=descending, field_to_sort=field_to_sort, log=log)
    
    # return
    return list_result


def translate_trapi_results(map_trapi, endpont_infores=None, num_limit=100, sort=True, descending=True, field_to_sort=None, log=False):
    '''
    will translate trapui result to more condensed format
    '''
    # initialize
    extracted_edges = []

    # extract
    trapi_message = map_trapi.get("message", {})
    if trapi_message and type(trapi_message) == dict:
        trapi_kg = trapi_message.get("knowledge_graph", {})
        if trapi_kg:
            # edges = map_trapi.get("message", {}).get("knowledge_graph", {}).get("edges", {})
            # nodes = map_trapi.get("message", {}).get("knowledge_graph", {}).get("nodes", {})
            edges = trapi_kg.get('edges', {})
            nodes = trapi_kg.get('nodes', {})

            # extract the nodes
            extracted_edges = []
            for edge_id, edge_data in edges.items():
                source = None
                target = None
                publications = []
                score = None
                pValue = None
                level = None
                reliability = None
                primarySource = {}

                source_id = edge_data.get(cutils.TRAPI_KEY_SUBJECT)
                target_id = edge_data.get(cutils.TRAPI_KEY_OBJECT)

                if nodes.get(source_id) and nodes.get(target_id):
                    source = {cutils.KEY_ID: source_id, cutils.KEY_NAME: nodes.get(source_id, {}).get(cutils.TRAPI_KEY_NAME, {})}
                    target = {cutils.KEY_ID: target_id, cutils.KEY_NAME: nodes.get(target_id, {}).get(cutils.TRAPI_KEY_NAME, {})}

                    # get publications and scores
                    for attribute in edge_data.get(cutils.TRAPI_KEY_ATTRIBUTES, []):
                        if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_PUBLICATIONS:
                            publications = attribute.get(cutils.TRAPI_KEY_VALUE, [])

                        if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_SCORE or attribute.get(cutils.TRAPI_KEY_ORIGINAL_NAME, "") == cutils.KEY_SCORE:
                            score = attribute.get(cutils.TRAPI_KEY_VALUE, "")

                        if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_P_VALUE:
                            pValue = attribute.get(cutils.TRAPI_KEY_VALUE, "")

                        if attribute.get(cutils.TRAPI_KEY_ORIGINAL_NAME, "") == cutils.TRAPI_KEY_LEVEL:
                            level = attribute.get(cutils.TRAPI_KEY_VALUE, "")

                        if attribute.get(cutils.TRAPI_KEY_ORIGINAL_NAME, "") == cutils.TRAPI_KEY_RELIABILITY:
                            reliability = attribute.get(cutils.TRAPI_KEY_VALUE, "")

                    # get the primary source
                    for knowledgeSource in edge_data.get(cutils.TRAPI_KEY_SOURCES, []):
                        if knowledgeSource.get(cutils.TRAPI_KEY_ATTR_RESOURCE_ROLE, "") == cutils.TRAPI_VALUE_PRIMARY_SOURCE:
                            primarySource = knowledgeSource.get(cutils.TRAPI_KEY_ATTR_RESOURCE_ID, None)


                    predicate = edge_data.get(cutils.TRAPI_KEY_PREDICATE)
                    edge_result = {cutils.KEY_SUBJECT: source, cutils.KEY_OBJECT: target, cutils.KEY_RELATIONSHIP: predicate}

                    # add properties
                    if len(publications) > 0:
                        edge_result[cutils.KEY_PUBLICATIONS] = publications

                    if score:
                        edge_result[cutils.KEY_SCORE] = score

                    if pValue:
                        edge_result[cutils.KEY_P_VALUE] = pValue

                    if level and reliability:
                        edge_result[cutils.KEY_LEVEL] = level
                        edge_result[cutils.KEY_RELIABILITY] = reliability

                    if primarySource:
                        edge_result[cutils.KEY_PRIMARY_SOURCE] = primarySource

                    if endpont_infores:
                        edge_result[cutils.KEY_TRAPI_SOURCE] = endpont_infores

                    # add edge
                    extracted_edges.append(edge_result)

    # see if need to sort
    if field_to_sort and sort and len(extracted_edges) > 0:
        sorted_elements = sorted(extracted_edges, key=lambda x: x.get(field_to_sort, 0), reverse=descending)
        extracted_edges = sorted_elements
   
    # return
    return extracted_edges[0:num_limit]


def query_trapi_list_for_string(list_endpoint_url, entity_name, list_ontologies, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], 
                           sort=True, descending=False, field_to_sort=None, log=False):
    '''
    query name resolver first for curies, then the service itself an translate
    '''
    # initialize
    map_trapi_response = {}
    list_result = []
    list_curies = []
    list_total_results = []

    # get the list of curies
    list_curies = get_curies(entity_name=entity_name, list_ontologies=list_ontologies, log=log)

    # log
    if True:
        print("for list of curies for: {} of {}".format(entity_name, list_curies))

    if len(list_curies) > 0:
        # loop through trapi URLS
        for url_trapi in list_endpoint_url:
            # log
            # print("querying endpoint: {}".format(url_trapi))

            # do the trapi query
            map_trapi_response = query_trapi_rest_service(endpoint_url=url_trapi, list_target=list_curies, list_predicates=list_predicates, 
                                                        list_source_types=list_source_types, list_target_types=list_target_types, log=False)
            
            # log
            if log:
                print("translating trapi result: \n{}".format(json.dumps(map_trapi_response, indent=2)))
            
            # translate
            list_result = translate_trapi_results(map_trapi=map_trapi_response, sort=sort, descending=descending, field_to_sort=field_to_sort, log=log)

            # log
            print("got num result: {} for: {}".format(len(list_result), url_trapi))

            # add to results
            list_total_results = list_total_results + list_result

    
    # log total results returns
    print("returning for curies: {}, total results: {}".format(list_curies, len(list_total_results)))

    # return
    return list_total_results


def query_trapi_map_for_string(map_endpoint_url, entity_name, list_ontologies, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], 
                           sort=True, descending=False, field_to_sort=None, log=False):
    '''
    query name resolver first for curies, then the service itself an translate
    '''
    # initialize
    map_trapi_response = {}
    list_result = []
    list_curies = []
    list_total_results = []

    # get the list of curies
    list_curies = get_curies(entity_name=entity_name, list_ontologies=list_ontologies, log=log)

    # log
    if True:
        print("for list of curies for: {} of {}".format(entity_name, list_curies))

    if len(list_curies) > 0:
        # loop through trapi URLS
        for infores_trapi, url_trapi in map_endpoint_url.items():
            # log
            # print("querying infores: {} with endpoint: {}".format(infores_trapi, url_trapi))

            # do the trapi query
            map_trapi_response = query_trapi_rest_service(endpoint_url=url_trapi, list_target=list_curies, list_predicates=list_predicates, 
                                                        list_source_types=list_source_types, list_target_types=list_target_types, log=False)
            
            # log
            if log:
                print("translating trapi result: \n{}".format(json.dumps(map_trapi_response, indent=2)))
            
            # translate
            list_result = translate_trapi_results(map_trapi=map_trapi_response, sort=sort, descending=descending, field_to_sort=field_to_sort, endpont_infores=infores_trapi, log=log)

            # log
            print("got num result: {} for: {}".format(len(list_result), infores_trapi))

            # add to results
            list_total_results = list_total_results + list_result

    
    # log total results returns
    print("returning for curies: {}, total results: {}".format(list_curies, len(list_total_results)))

    # return
    return list_total_results


def query_all_trapi_for_string(entity_name, list_ontologies, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], 
                           sort=True, descending=False, field_to_sort=None, log=False):
    '''
    query name resolver first for curies, then the service itself an translate
    '''
    # initialize
    map_trapi_all = cutils.MAP_URL_ALL

    # TODO - filter KP map by query triple
    
    # get the results
    list_total_results = query_trapi_map_for_string(map_endpoint_url=map_trapi_all, entity_name=entity_name, list_ontologies=list_ontologies, list_predicates=list_predicates, 
                                                    list_source_types=list_source_types,
                                                    list_target_types=list_target_types, sort=sort, descending=descending, field_to_sort=field_to_sort, log=log)

    # return
    return list_total_results


# main
if __name__ == "__main__":
    # initialize
    id_source = ["ChEMBL:CHEMBL17"]
    list_chem_types = ["biolink:SmallMolecule"]
    list_disease_types = ["biolink:Disease"]
    entity_name = "type 2 diabetes"
    list_ontologies = ['MONDO']
    list_t2d_id = ["MONDO:0005148"]

    # # test method
    # map_trapi_result = query_trapi_rest_service(endpoint_url=URL_MOLEPRO, list_source=id_source, list_source_types=list_source_types, list_target_types=list_target_types, log=True)

    # map_result = translate_trapi_results(map_trapi=map_trapi_result, log=True)
    # print("got result: \n{}".format(json.dumps(map_result, indent=2)))

    # test name reslver call
    list_ids = get_curies(entity_name=entity_name, list_ontologies=list_ontologies, log=True)

    # test end to end query
    map_result = query_trapi_for_string(endpoint_url=cutils.URL_MOLEPRO, entity_name=entity_name, list_ontologies=list_ontologies, 
                                        list_source_types=list_chem_types, list_target_types=list_disease_types, log=True)
    print("got result: \n{}".format(json.dumps(map_result, indent=2)))
