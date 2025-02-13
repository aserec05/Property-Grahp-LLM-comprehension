"""Test module."""

import json
from langchain_ollama import ChatOllama
import libs.graph_management as g
import libs.pipelines as p

model = ChatOllama(model="llama3.2")

def run_pipeline_one(n_run: int):
    print("--- PIPELINE 1 ---")
    with open('requests/queries.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    #print(len(encoded_graph))
    path = 'results/pipeline_1/'
    for j in range(n_run):
        i=0
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+str(j+1)+'.txt', 'w') as file:
                file.write('')
        for q in queries:
            i+=1
            print(f"request {i}:")
            res = p.pipeline_pydantic(encoded_graph, "Incident", q)
            print("-------------------")
            with open(path+str(j+1)+'.txt', 'a') as file:
                file.write(str(res) + '\n---\n')


def run_pipeline_two(n_run: int):
    print("--- PIPELINE 2 ---")
    with open('requests/nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/wc_schema.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    path = 'results/pipeline_2/'
    for j in range(n_run):
        i=0
        with open(path+str(j+1)+'.txt', 'w') as file:
                file.write('')
        for q in queries:
            i+=1
            print(f"request {i}:")
            res = p.pipeline_NL_to_query(data, "json", q)
            print("-------------------")
            with open(path+str(j+1)+'.txt', 'a') as file:
                file.write(res + '\n---\n')
            
def run_pipeline_three(n_run: int):
    print("--- PIPELINE 3 ---")
    with open('requests/nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    #print(len(encoded_graph))
    path = 'results/pipeline_3/'
    for j in range(n_run):
        i=0
        with open(path+str(j+1)+'.txt', 'w') as file:
                file.write('')
        for q in queries:
            i+=1
            print(f"request {i}:") 
            res = p.pipeline_NL_to_res(encoded_graph, "Incident", q)
            print("-------------------")
            with open(path+str(j+1)+'.txt', 'a') as file:
                file.write(str(res) + '\n---\n')

if __name__ == "__main__":
    n_run = 3
    run_pipeline_one(n_run)
    run_pipeline_two(n_run)
    run_pipeline_three(n_run)
