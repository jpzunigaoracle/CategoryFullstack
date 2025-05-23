# config.py
# Author: Ansh

DB_TYPE = "qdrant"  # Options: "oracle", "qdrant"

# OracleDB Configuration
ORACLE_DB_USER = "ansh"  #Enter your oracle vector Db username
ORACLE_DB_PWD = "Gena#######"  #Enter your oracle vector Db password
ORACLE_DB_HOST_IP = "######"  #Enter your oracle vector Db host ip
ORACLE_DB_PORT = 1521   #Enter your oracle vector Db host port
ORACLE_DB_SERVICE = "orclpdb01.sub05101349370.bpivcnllm.oraclevcn.com" 

ORACLE_USERNAME = ORACLE_DB_USER
ORACLE_PASSWORD = ORACLE_DB_PWD
ORACLE_DSN = f"{ORACLE_DB_HOST_IP}:{ORACLE_DB_PORT}/{ORACLE_DB_SERVICE}"
ORACLE_TABLE_NAME = "policyTable" #name of table where you want to store the embeddings in oracle DB

# Qdrant Configuration
QDRANT_LOCATION = ":memory:"
QDRANT_COLLECTION_NAME = "my_documents" #name of table where you want to store the embeddings in qdrant DB
QDRANT_DISTANCE_FUNC = "Dot"

# Common Configuration
USER_ID =""
AUTH_TYPE="API_KEY"
CONFIG_PROFILE="DEFAULT"
OBJECT_STORAGE_LINK = "https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/##############/b/##########/o/"
DIRECTORY = 'data'  # directory to store the pdf's from where the RAG model should take the documents from
PROMPT_CONTEXT = "You are an AI Assistant trained to give answers based only on the information provided. Given only the above text provided and not prior knowledge, answer the query. If someone asks you a question and you don't know the answer, don't try to make up a response, simply say: I don't know."

ENDPOINT= "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com" #change in case you want to select a diff region
EMBEDDING_MODEL = "cohere.embed-multilingual-v3.0"
GENERATE_MODEL = "cohere.command-r-08-2024"  # cohere.command-r-16k or cohere.command-r-plus
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaaohqhsft2n2hbefl7pushupe6zcel4b2hzpgotevssjrz57nf5fia"

# COHERE
PROVIDER_COHERE = "cohere"
EMBEDDING_MODEL_COHERE = "cohere.embed-multilingual-v3.0"
GENERATE_MODEL_COHERE = "cohere.command-r-plus-08-2024"

# LLAMA data
PROVIDER_LLAMA="meta"
GENERATE_MODEL_LLAMA_33 = "ocid1.generativeaimodel.oc1.eu-frankfurt-1.amaaaaaask7dceya4tdabclcsqbc3yj2mozvvqoq5ccmliv3354hfu3mx6bq"