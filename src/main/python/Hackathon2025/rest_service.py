
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
    list_gene: List[str] = Query(..., description="PPARG")
    ):
    print("for: %s, got gene input: %s", request.url.path, list_gene)

    # call your new method that takes a list of strings
    list_result = dutils.get_list_disease_for_gene_list(gene_list=list_gene)

    return JSONResponse(content={"result": list_result})


