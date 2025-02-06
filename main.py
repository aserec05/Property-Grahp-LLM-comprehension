"""Test module."""

import json
from langchain_ollama import ChatOllama
import libs.graph_management as g
import libs.pipelines as p

model = ChatOllama(model="llama3.2")

def run_pipeline_one():
    with open('requests/queries.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    print(len(encoded_graph))
    i=0
    with open('results/llm_results_one.txt', 'w') as file:
        file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_pydantic(encoded_graph, "Incident", q)
        print("-------------------")
        with open('results/llm_results_one.txt', 'a') as file:
            file.write(str(res) + '\n---\n')


def run_pipeline_two():
    with open('requests/nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/wc_schema.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    i=0
    with open('results/llm_results_two.txt', 'w') as file:
        file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_NL_to_query(data, "json", q)
        print("-------------------")
        with open('results/llm_results_two.txt', 'a') as file:
            file.write(res + '\n---\n')
            
def run_pipeline_three():
    with open('requests/nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('data/sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    print(len(encoded_graph))
    i=0
    with open('results/llm_results_three.txt', 'w') as file:
        file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_NL_to_res(encoded_graph, "Incident", q)
        print("-------------------")
        with open('results/llm_results_three.txt', 'a') as file:
            file.write(str(res) + '\n---\n')

if __name__ == "__main__":
    run_pipeline_one()
    run_pipeline_two()
    run_pipeline_three()
