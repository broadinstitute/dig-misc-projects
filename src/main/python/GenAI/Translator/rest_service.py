
# imports
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import constants_utils as cutils

from trapi_utils import query_trapi_for_string

# constants
app = FastAPI()

# methods
@app.get("/get_drug_for_disease")
def reverse_string(input: str = Query(..., description="String to reverse")):
    # call the method
    # reversed_str = input[::-1]
    print("got input: {}".format(input))
    list_result = query_trapi_for_string(endpoint_url=cutils.URL_MOLEPRO, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_TREATS, list_source_types=cutils.LIST_ENTITIES_DRUG, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, log=True)    
    # return
    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_disease")
def reverse_string(input: str = Query(..., description="String to reverse")):
    # call the method
    # reversed_str = input[::-1]
    print("got input: {}".format(input))
    list_result = query_trapi_for_string(endpoint_url=cutils.URL_GENETICSKP, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, log=True)    
    # return
    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})




