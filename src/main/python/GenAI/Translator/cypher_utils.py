
# imports
from neo4j import GraphDatabase
from typing import List, Dict
import os


# constants
NEO4J_IP_PORT = 'localhost:7887'
if os.getenv('NEO4J_IP_PORT'):
    NEO4J_IP_PORT = os.getenv('NEO4J_IP_PORT')
NEO4J_URI = "bolt://{}".format(NEO4J_IP_PORT)
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


# Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# methods
def run_cypher(cypher_query: str, log=False):
    '''
    queries a neo4j database
    '''
    # initialize
    list_result = []
    message = "all good"
    query = cypher_query.strip()

    # log
    if log:
        print("running query: \n{}".format(cypher_query))

    # make sure have neo4j parameters
    if NEO4J_IP_PORT and NEO4J_USER and NEO4J_PASSWORD:
        # execute the query    
        try:
            # read only for driver < 5
            # with driver.session(config=SessionConfig(default_access_mode="READ")) as session:
            # read only for driver versino >=5
            with driver.session(default_access_mode="r") as session:        
                cypher_result = session.run(query)
                # Convert each record to a dictionary
                list_result = [record.data() for record in cypher_result]
            
        except Exception as e:
            message = str(e)
            # raise HTTPException(status_code=500, detail=str(e))

    else:
        message = 'no connected'

    # build the json
    result = {'data': list_result, 'message': message}

    # return
    return result

