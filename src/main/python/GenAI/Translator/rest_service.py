
# imports
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import constants_utils as cutils

from trapi_utils import query_trapi_for_string, query_trapi_list_for_string

# constants
# app = FastAPI()
app = FastAPI(root_path="/")

# methods
@app.get("/get_drug_for_disease")
def get_drug_for_disease(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    # list_result = query_trapi_for_string(endpoint_url=cutils.URL_MOLEPRO, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
    #                                      list_predicates=cutils.LIST_PREDICATES_TREATS, list_source_types=cutils.LIST_ENTITIES_DRUG, 
    #                                      list_target_types=cutils.LIST_ENTITIES_DISEASE, log=False)    

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_TREATS, list_source_types=cutils.LIST_ENTITIES_DRUG, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_disease")
def get_gene_for_disease(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    # list_result = query_trapi_for_string(endpoint_url=cutils.URL_GENETICSKP, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
    #                                      list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
    #                                      list_target_types=cutils.LIST_ENTITIES_DISEASE, 
    #                                      field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    


    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, 
                                         field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_disease_automat")
def get_gene_for_disease_automat(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_for_string(endpoint_url=cutils.URL_AUTOMAT, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, 
                                         field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    
    # return
    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_pathway_for_disease")
def get_pathway_for_disease(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    # list_result = query_trapi_for_string(endpoint_url=cutils.URL_GENETICSKP, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
    #                                      list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_PATHWAY, 
    #                                      list_target_types=cutils.LIST_ENTITIES_DISEASE, 
    #                                      field_to_sort=cutils.KEY_P_VALUE, descending=False, log=False)    

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_PATHWAY, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, 
                                         field_to_sort=cutils.KEY_P_VALUE, descending=False, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_drug_for_gene")
def get_drug_for_gene(request: Request, input: str = Query(..., description="gene")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    # list_result = query_trapi_for_string(endpoint_url=cutils.URL_MOLEPRO, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
    #                                      list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DRUG, 
    #                                      list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DRUG, 
                                         list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_cell_for_gene")
def get_cell_for_gene(request: Request, input: str = Query(..., description="gene")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    # list_result = query_trapi_for_string(endpoint_url=cutils.URL_SPOKE, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
    #                                      list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_CELL, 
    #                                      list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_CELL, 
                                         list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


