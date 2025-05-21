

# keys for result
KEY_ID = "id"
KEY_NAME = "name"
KEY_PROPERTIES = "propterties"
KEY_PUBLICATIONS = "pubmed_ids"
KEY_SCORE = "score"
KEY_P_VALUE = "p-value"
KEY_LEVEL = "level"
KEY_RELIABILITY = "reliability"

KEY_SUBJECT = "subject"
KEY_SUBJECT_TYPE = "subject_type"
KEY_SUBJECT_PROPS = "subject_properties"

KEY_OBJECT = "object"
KEY_OBJECT_TYPE = "object_type"
KEY_OBJECT_PROPS = "object_properties"

KEY_RELATIONSHIP = "relationship"
KEY_RELATIONSHIP_PROPS = "relationship_properties"
KEY_PRIMARY_SOURCE = "primary_knowledge_source"
KEY_TRAPI_SOURCE = "knowledge_provider"


# TRAPI KEYS
TRAPI_KEY_PREDICATE = "predicate"
TRAPI_KEY_SUBJECT = "subject"
TRAPI_KEY_OBJECT = "object"
TRAPI_KEY_VALUE = "value"
TRAPI_KEY_NAME = "name"
TRAPI_KEY_SCORE = "score"
TRAPI_KEY_SCORE = "p-value"
TRAPI_KEY_ATTRIBUTES = "attributes"
TRAPI_KEY_ATTRIBUTE_TYPE_ID = "attribute_type_id"
TRAPI_KEY_ORIGINAL_NAME = "original_attribute_name"
TRAPI_KEY_LEVEL = "level"
TRAPI_KEY_RELIABILITY = "reliability"
TRAPI_KEY_SOURCES = "sources"
TRAPI_VALUE_PRIMARY_SOURCE = "primary_knowledge_source"
TRAPI_KEY_ATTR_RESOURCE_ROLE = "resource_role"
TRAPI_KEY_ATTR_RESOURCE_ID = "resource_id"


# URLS
URL_MOLEPRO = "https://translator.broadinstitute.org/molepro/trapi/v1.5"
URL_GENETICSKP = "https://genetics-kp.ci.transltr.io/genetics_provider/trapi/v1.5"
URL_AUTOMAT = "https://automat.ci.transltr.io/pharos"
URL_SPOKE = "https://spokekp.transltr.io/api/v1.5"
URL_FDA = "https://multiomics.rtx.ai:9990/dakp"
URL_RTX_KG2 = "https://kg2cploverdb.transltr.io"
URL_MULTIOMICS = "https://multiomics.transltr.io/mokp"
URL_MICROBIOME = "https://multiomics.transltr.io/mbkp"
URL_COHD = "https://cohd-api.transltr.io/api"
URL_ROBOKOP = "https://automat.transltr.io/robokopkg"
URL_CLINICAL = "https://automat.renci.org/ehr-clinical-connections-kp"
# dropped
URL_CONNECTIONS = "https://chp-api.transltr.io" # only genes to tissue
URL_SERVICE_PROVIDER = "https://bte.transltr.io/v1/team/Service%20Provider" # not working


# INFORES
INFORES_MOLEPRO = "infores:molepro"
INFORES_GENETICSKP = "infores:genetics-data-provider"
INFORES_AUTOMAT = "infores:automat-pharos"
INFORES_SPOKE = "infores:spoke"
INFORES_FDA = "infores:multiomics-drugapprovals"
INFORES_RTX_KG2 = "infores:rtx-kg2"
INFORES_MULTIOMICS = "infores:multiomics-multiomics"
INFORES_MICROBIOME = "infores:multiomics-microbiome"
INFORES_COHD = "infores:cohd"
INFORES_ROBOKOP = "infores:automat-robokop"
INFORES_CLINICAL = "infores:multiomics-clinicaltrials"

# URL LISTS
LIST_URL_ALL = [
    URL_MOLEPRO, URL_GENETICSKP, URL_AUTOMAT, URL_SPOKE, URL_FDA, 
    URL_RTX_KG2, URL_MULTIOMICS, URL_MICROBIOME, URL_CLINICAL, URL_COHD
]

MAP_URL_ALL = {
    INFORES_MOLEPRO: URL_MOLEPRO, INFORES_GENETICSKP: URL_GENETICSKP, INFORES_AUTOMAT: URL_AUTOMAT, INFORES_SPOKE: URL_SPOKE, INFORES_FDA: URL_FDA, 
    INFORES_RTX_KG2: URL_RTX_KG2, INFORES_MULTIOMICS: URL_MULTIOMICS, INFORES_MICROBIOME: URL_MICROBIOME, INFORES_CLINICAL: URL_CLINICAL, INFORES_COHD: URL_COHD
}


# TODO - drug/disease
LIST_URL_DRUG_DISEASE = [URL_MOLEPRO, URL_AUTOMAT, URL_FDA, URL_RTX_KG2]
# TODO - gene/disease
LIST_URL_GENE_DISEASE = [URL_GENETICSKP, URL_RTX_KG2]
# TODO - gene/drug
LIST_URL_DRUG_GENE = [URL_MOLEPRO, URL_RTX_KG2]
# TODO - drug/pathway
LIST_URL_DRUG_PATHWAY = [URL_MOLEPRO, URL_RTX_KG2]
# TODO - gene/gene
LIST_URL_GENE_GENE = [URL_RTX_KG2, URL_MOLEPRO]
# TODO - drug/cell
LIST_URL_DRUG_TISSUE = [URL_RTX_KG2]
# TODO - drug/drug
LIST_URL_DRUG_DRUG = [URL_RTX_KG2]
# TODO - pathway/disease
LIST_URL_PATHWAY_DISEASE = [URL_GENETICSKP, URL_RTX_KG2]
# TODO - tissue/disease
LIST_URL_TISSUE_DISEASE = [URL_RTX_KG2]
# TODO - gene/tissue
LIST_URL_GENE_TISSUE = [URL_RTX_KG2, URL_MOLEPRO]



# LISTS
LIST_ONTOLOGIES_DISEASE = ["MONDO"]
LIST_ONTOLOGIES_GENE = ["NCBIGene"]
LIST_ONTOLOGIES_CHEM = ["CHEBI"]
LIST_ONTOLOGIES_PATHWAY = ["GO"]
LIST_ONTOLOGIES_CELL = ["UBERON", "UMLS", "CL"]

LIST_PREDICATES_TREATS = ["biolink:treats"]
LIST_PREDICATES_RELATED_TO = ["biolink:related_to"]

LIST_ENTITIES_GENE = ["biolink:Gene"]
LIST_ENTITIES_DISEASE = ["biolink:Disease"]
LIST_ENTITIES_DRUG = ["biolink:SmallMolecule"]
LIST_ENTITIES_PATHWAY = ["biolink:Pathway"]
LIST_ENTITIES_CELL = ["biolink:Cell"]

BIOLINK_PUBLICATIONS = "biolink:publications"
BIOLINK_SCORE = "biolink:score"
BIOLINK_P_VALUE = "biolink:p-value"

