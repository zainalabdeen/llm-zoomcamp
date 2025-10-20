from data_ingestion import connect_to_index
from search_process import prepare_search , query_without_llm, query_with_llm

def connect_to_qdrant():
    return prepare_search() 

def retrieve_answers(query: str,prepared_dict):
    return query_without_llm(prepared_dict['index'],prepared_dict['bm25'],prepared_dict['corpus_items'], query)

def generate_final_answer(query: str, results):
    return query_with_llm(query, results)
