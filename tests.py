"""Test module."""

import os
import json
import graph_management as g
import pipelines as p
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.2")

def run_pipeline_one():
    with open('queries.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    print(len(encoded_graph))
    i=0
    with open('llm_results_one.txt', 'w') as file:
            file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_pydantic(encoded_graph, "Incident", q)
        print("-------------------")
        with open('llm_results_one.txt', 'a') as file:
            file.write(str(res) + '\n---\n')


def run_pipeline_two():
    with open('nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('wc_schema.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    i=0
    with open('llm_results_two.txt', 'w') as file:
            file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_NL_to_query(data, "json", q)
        print("-------------------")
        with open('llm_results_two.txt', 'a') as file:
            file.write(res + '\n---\n')
            
def run_pipeline_three():
    with open('nl_request.txt', 'r', encoding='utf-8-sig') as file:
        queries = file.readlines()
    with open('sub_graph_wc_1.json', 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)
    encoded_graph = g.encode_graph(g.create_graph_for_sub_wc(data))
    print(len(encoded_graph))
    i=0
    with open('llm_results_three.txt', 'w') as file:
            file.write('')
    for q in queries:
        i+=1
        print(f"request {i}:")
        res = p.pipeline_NL_to_res(encoded_graph, "Incident", q)
        print("-------------------")
        with open('llm_results_three.txt', 'a') as file:
            file.write(str(res) + '\n---\n')

if __name__ == "__main__":
    run_pipeline_one()
    run_pipeline_two()
    run_pipeline_three()
