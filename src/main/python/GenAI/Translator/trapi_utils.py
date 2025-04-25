
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
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")

    # return
    return response.json()


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


def query_trapi_for_string(endpoint_url, entity_name, list_ontologies, list_predicates=["biolink:related_to"], list_source_types=[], list_target_types=[], log=False):
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
        list_result = translate_trapi_results(map_trapi=map_trapi_response, log=log)
    
    # return
    return list_result


def translate_trapi_results(map_trapi, log=False):
    '''
    will translate trapui result to more condensed format
    '''
    edges = map_trapi.get("message", {}).get("knowledge_graph", {}).get("edges", {})
    nodes = map_trapi.get("message", {}).get("knowledge_graph", {}).get("nodes", {})

    # extract the nodes
    
    extracted_edges = []
    for edge_id, edge_data in edges.items():
        source = None
        target = None
        publications = []
        score = None
        pValue = None

        source_id = edge_data.get(cutils.TRAPI_KEY_SUBJECT)
        target_id = edge_data.get(cutils.TRAPI_KEY_OBJECT)

        if nodes.get(source_id) and nodes.get(target_id):
            source = {cutils.KEY_ID: source_id, cutils.KEY_NAME: nodes.get(source_id, {}).get(cutils.TRAPI_KEY_NAME, {})}
            target = {cutils.KEY_ID: target_id, cutils.KEY_NAME: nodes.get(target_id, {}).get(cutils.TRAPI_KEY_NAME, {})}

            # get publications and scores
            for attribute in edge_data.get(cutils.TRAPI_KEY_ATTRIBUTES, []):
                if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_PUBLICATIONS:
                    publications = attribute.get(cutils.TRAPI_KEY_VALUE, [])

                if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_SCORE:
                    score = attribute.get(cutils.TRAPI_KEY_VALUE, [])

                if attribute.get(cutils.TRAPI_KEY_ATTRIBUTE_TYPE_ID, "") == cutils.BIOLINK_P_VALUE:
                    pValue = attribute.get(cutils.TRAPI_KEY_VALUE, [])

            predicate = edge_data.get(cutils.TRAPI_KEY_PREDICATE)
            edge_result = {cutils.KEY_SUBJECT: source, cutils.KEY_OBJECT: target, cutils.KEY_RELATIONSHIP: predicate}

            # add properties
            if len(publications) > 0:
                edge_result[cutils.KEY_PUBLICATIONS] = publications

            if score:
                edge_result[cutils.KEY_SCORE] = score

            if pValue:
                edge_result[cutils.KEY_P_VALUE] = pValue

            # add edge
            extracted_edges.append(edge_result)
    
    return extracted_edges
    

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
