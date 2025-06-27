
# imports
from typing import List
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse


import data_utils as dutils

# constants
# app = FastAPI()
app = FastAPI(root_path="/")
logger = dutils.get_logger(__name__)


# methods
@app.get("/get_diseases_for_gene_list")
def get_diseases_for_genes(
    request: Request,
    list_gene: str = Query(..., description="PPARG")
    ):
    print("for: {}, got gene input: {}".format(request.url.path, list_gene))

    # get the list
    list_for_method = safe_split(string_input=list_gene)

    # call your new method that takes a list of strings
    list_result = dutils.get_list_disease_for_entity_list(list_input=list_for_method)

    return JSONResponse(content={"result": list_result})



@app.get("/get_diseases_for_pheno_list")
def get_diseases_for_genes(
    request: Request,
    list_phenotype: str = Query(..., description="HP.101010")
    ):
    print("for: {}, got gene input: {}".format(request.url.path, list_phenotype))

    # get the list
    list_for_method = safe_split(string_input=list_phenotype)

    # call your new method that takes a list of strings
    list_result = dutils.get_list_disease_for_entity_list(list_input=list_for_method, for_genes=False)

    return JSONResponse(content={"result": list_result})


def safe_split(string_input, delimiter=','):
    """
    Split a string by delimiter, returning empty list for empty/None strings
    """
    if not string_input or string_input.strip() == '':
        return []
    
    # get split list
    list_split = [item.strip() for item in string_input.split(delimiter)]

    # log
    print("for input:  {}, got string list of: {}".format(string_input, list_split))

    # return
    return list_split
