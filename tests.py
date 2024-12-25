"""Test module."""

from typing import Optional
import json
import networkx as nx
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


model = ChatOllama(model="llama3.2")


def test1():
    messages = [
        SystemMessage("Translate the following from English into Italian"),
        HumanMessage("hi!"),
    ]
    response = model.invoke(messages)
    print(response.content)


def test2():
    system_template = "Translate exactly the following from English into {language}"
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")])
    prompt = prompt_template.invoke({"language": "Italian", "text": "hi!"})
    print(prompt.to_messages())
    response = model.invoke(prompt)
    print(response.content)


# Pydantic
class TranslationRequest(BaseModel):
    translation: str = Field(..., description="The translation of the text")
    targate_langugage: str= Field(..., description="target language")

def test3():
    structured_model = model.with_structured_output(TranslationRequest)
    messages = [
        SystemMessage("Translate the text to french"),
        HumanMessage("hi!"),
    ]
    response = structured_model.invoke(messages)
    print(response)

def pipeline(graph, format_graph, query):
    system_template = "Here is a graph in the {format} format : {graph}."
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{query}")])
    prompt = prompt_template.invoke({
        "format" : format_graph,
        "graph": graph,
        "query": query
    })
    prompt.to_messages()
    response = model.invoke(prompt)
    print(response.usage_metadata)
    print(response.content)

def create_graph_for_wc(data):
    graph = nx.Graph()
    for item in data:
        node_n = item['n']
        graph.add_node(node_n['identity'], labels=node_n['labels'], **node_n['properties'])

        node_m = item['m']
        graph.add_node(node_m['identity'], labels=node_m['labels'], **node_m['properties'])

        edge_r = item['r']
        graph.add_edge(edge_r['start'], edge_r['end'], id=edge_r['identity'], label=edge_r['type'], **edge_r['properties'])
    return graph

def create_graph_for_sub_wc(data):
    graph = nx.Graph()

    for entry in data:
        main_node = entry['p']
        graph.add_node(
            main_node['identity'], 
            labels=main_node['labels'], 
            **main_node['properties']
        )

        for related_node in entry['relatedNodes']:
            graph.add_node(
                related_node['identity'], 
                labels=related_node['labels'], 
                **related_node['properties']
            )

        for relationship in entry['relationships']:
            graph.add_edge(
                relationship['start'], 
                relationship['end'], 
                id=relationship['identity'], 
                label=relationship['type'], 
                **relationship['properties']
            )
    return graph

def create_node_string(graph):
    node_descriptions = []
    for node, props in graph.nodes(data=True):
        labels = props.pop('labels', [])
        labels_str = ', '.join(labels)
        prop_desc = ', '.join([f"{key}: {value}" for key, value in props.items()])
        node_descriptions.append(f"{node} [{labels_str}] ({prop_desc})")
    return ', '.join(node_descriptions)

def encode_graph(graph):
    nodes_string = create_node_string(graph)
    output = "G describes a graph among nodes: \n%s.\n" % nodes_string
    if graph.edges():
        output += "In this graph:\n"
    for source_node in graph.nodes():
        target_nodes = list(graph.neighbors(source_node))
        target_nodes_str = ""
        nedges = 0
        for target_node in target_nodes:
            edge_props = graph.get_edge_data(source_node, target_node)
            edge_props_str = ', '.join([f"{key}: {value}" for key, value in edge_props.items()])
            target_nodes_str += f"{target_node} ({edge_props_str}), "
            nedges += 1
        if nedges > 1:
            output += "Node %s is connected to nodes %s.\n" % (
                source_node,
                target_nodes_str[:-2],
            )
        elif nedges == 1:
            output += "Node %s is connected to node %s.\n" % (
                source_node,
                target_nodes_str[:-2],
            )
    return output

if __name__ == "__main__":
    file_path = 'sub_graph_wc_1.json'
    with open(file_path, 'r',  encoding='utf-8-sig') as file:
        data = json.load(file)

    graph = create_graph_for_sub_wc(data)
    encoded_graph = encode_graph(graph)
    print(len(encoded_graph))
    pipeline(encoded_graph, "Incident", "How many MATCHES Aline play ?")
