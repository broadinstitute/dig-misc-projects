
# imports
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import constants_utils as cutils
import cypher_utils as cyutils


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


@app.get("/get_disease_for_drug")
def get_disease_for_drug(request: Request, input: str = Query(..., description="drug")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_CHEM,
                                         list_predicates=cutils.LIST_PREDICATES_TREATS, list_source_types=cutils.LIST_ENTITIES_DISEASE, 
                                         list_target_types=cutils.LIST_ENTITIES_DRUG, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_disease")
def get_gene_for_disease(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))


    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, 
                                         field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    

    return JSONResponse(content={'result': list_result})


@app.get("/get_disease_for_gene")
def get_disease_for_gene(request: Request, input: str = Query(..., description="gene")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))


    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DISEASE, 
                                         list_target_types=cutils.LIST_ENTITIES_GENE, 
                                         field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    

    return JSONResponse(content={'result': list_result})

# @app.get("/get_gene_for_disease_automat")
# def get_gene_for_disease_automat(request: Request, input: str = Query(..., description="disease")):
#     # call the method
#     # reversed_str = input[::-1]
#     print("for: {}, got input: {}".format(request.url.path, input))
#     list_result = query_trapi_for_string(endpoint_url=cutils.URL_AUTOMAT, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
#                                          list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
#                                          list_target_types=cutils.LIST_ENTITIES_DISEASE, 
#                                          field_to_sort=cutils.KEY_SCORE, descending=True, log=False)    
#     # return
#     # return JSONResponse(content={"original": input, "reversed": reversed_str})
#     return JSONResponse(content={'result': list_result})


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


@app.get("/get_disease_for_pathway")
def get_disease_for_pathway(request: Request, input: str = Query(..., description="pathway")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_PATHWAY,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DISEASE, 
                                         list_target_types=cutils.LIST_ENTITIES_PATHWAY, 
                                         field_to_sort=cutils.KEY_P_VALUE, descending=False, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_drug_for_pathway")
def get_drug_for_pathway(request: Request, input: str = Query(..., description="pathway")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_PATHWAY,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DRUG, 
                                         list_target_types=cutils.LIST_ENTITIES_PATHWAY, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_pathway_for_drug")
def get_pathway_for_drug(request: Request, input: str = Query(..., description="drug")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_CHEM,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_PATHWAY, 
                                         list_target_types=cutils.LIST_ENTITIES_DRUG, log=False)    

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


@app.get("/get_gene_for_drug")
def get_drug_for_gene(request: Request, input: str = Query(..., description="drug")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_CHEM,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_DRUG, log=False)    

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

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_CELL, 
                                         list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_cell")
def get_gene_for_cell(request: Request, input: str = Query(..., description="cell")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_CELL,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_CELL, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_gene_for_gene")
def get_cell_for_gene(request: Request, input: str = Query(..., description="gene")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))

    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_GENE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ONTOLOGIES_GENE, 
                                         list_target_types=cutils.LIST_ENTITIES_GENE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_cell_for_disease")
def get_cell_for_gene(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_CELL, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_disease_for_cell")
def get_cell_for_gene(request: Request, input: str = Query(..., description="cell")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_CELL,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DISEASE, 
                                         list_target_types=cutils.LIST_ENTITIES_CELL, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})


@app.get("/get_disease_for_disease")
def get_cell_for_gene(request: Request, input: str = Query(..., description="disease")):
    # call the method
    # reversed_str = input[::-1]
    print("for: {}, got input: {}".format(request.url.path, input))
    list_result = query_trapi_list_for_string(list_endpoint_url=cutils.LIST_URL_ALL, entity_name=input, list_ontologies=cutils.LIST_ONTOLOGIES_DISEASE,
                                         list_predicates=cutils.LIST_PREDICATES_RELATED_TO, list_source_types=cutils.LIST_ENTITIES_DISEASE, 
                                         list_target_types=cutils.LIST_ENTITIES_DISEASE, log=False)    

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content={'result': list_result})








@app.get("/get_common_pathways")
def get_common_pathways(request: Request, input: str = Query(..., description="gene")):
    # cypher query
    query = '''
    MATCH (t1:Trait {id: 'T2D'})-[:TRAIT_FACTOR]-(f1:Factor)-[:FACTOR_GENE]-(g:Gene)-[:FACTOR_GENE]-(f2:Factor)-[:TRAIT_FACTOR]-(t2:Trait {id: 'AD'})
    RETURN 
        f1.id AS FactorT2D, 
        f1.label AS FactorT2DName, 
        collect(g.id) AS SharedGenes, 
        f2.id AS FactorALZ, 
        f2.label AS FactorALZName
    '''

    # log
    # print("running cypher query: \n{}".format(query))

    # call the method
    result = cyutils.run_cypher(cypher_query=query, log=True)

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content=result)


@app.get("/get_cypher_query")
def get_common_pathways(request: Request, input: str = Query(..., description="query")):
    # cypher query
    query = input

    # log
    # print("running cypher query: \n{}".format(query))

    # call the method
    result = cyutils.run_cypher(cypher_query=query, log=True)

    # return JSONResponse(content={"original": input, "reversed": reversed_str})
    return JSONResponse(content=result)
