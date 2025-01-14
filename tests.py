"""Test module."""

from typing import Optional
import os
import csv
import json
import networkx as nx
import pandas as pd
from typing import Optional, List, Dict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


model = ChatOllama(model="llama3.2")

# Pydantic model for structured output
class QueryResponse(BaseModel):
    query: str
    result: List[Dict] = Field(
        ..., description="List of result dictionaries where each dictionary represents a record."
    )

def enforce_strict_format(prompt: str, query: str) -> str:
    """
    Enforce a strict format for LLM responses.
    """
    return (
        f"{prompt}\n"
        "Respond strictly in this JSON format:\n"
        "{{\n"
        "    \"query\": \"<Generated Cypher query>\",\n"
        "    \"result\": [\n"
        "        {{\"property1\": \"value1\", \"property2\": \"value2\"}},\n"
        "        ...\n"
        "    ]\n"
        "}}\n"
        f"Query: {query}"
    )

def parse_llm_response(response_content: str) -> Optional[Dict]:
    """
    Parse the response from the LLM to ensure it matches the expected format.
    """
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        print("Invalid JSON format in response.")
        return None
    
def pipeline_pydantic(graph, format_graph, query):
    """
    Main pipeline function to interact with the LLM for graph queries.
    """
    system_template = "You are a Cypher inference engine. Here is a graph in the {format} format : {graph}."
    strict_prompt = enforce_strict_format(system_template, query)
    
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", strict_prompt), ("user", "{query}")]
    )
    prompt = prompt_template.invoke({
        "format": format_graph,
        "graph": graph,
        "query": query
    })
    
    parser = PydanticOutputParser(pydantic_object=QueryResponse)

    try:
        response = model.invoke(prompt)
        
        if response is None:
            print("Model invocation returned None. Check the model setup or input prompt.")
            return
        
        if not hasattr(response, 'content'):
            print("Response object does not have a 'content' attribute.")
            return
        
        parsed_response = parser.parse(response.content)
        print("Parsed response:", parsed_response)
    
    except Exception as e:
        print(f"Error during model invocation or response parsing: {e}")

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

def create_graph_for_synthea(folder):
    """Create a graph from Synthea CSV files based on provided schemas."""
    graph = nx.Graph()
    
    # Paths to key Synthea files
    patient_file = os.path.join(folder, 'patients.csv')
    encounter_file = os.path.join(folder, 'encounters.csv')
    condition_file = os.path.join(folder, 'conditions.csv')
    medication_file = os.path.join(folder, 'medications.csv')
    
    # Read patients
    patient_ids = {}
    if os.path.exists(patient_file):
        with open(patient_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['Id']
                patient_name = f"Patient_{patient_id}"
                graph.add_node(patient_name, type='patient', data=row)
                patient_ids[patient_id] = patient_name

    # Read encounters
    if os.path.exists(encounter_file):
        with open(encounter_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                encounter_id = row['Id']
                patient_id = row['PATIENT']
                if patient_id in patient_ids:
                    encounter_name = f"Encounter_{encounter_id}"
                    graph.add_node(encounter_name, type='encounter', data=row)
                    graph.add_edge(patient_ids[patient_id], encounter_name)

    # Read conditions
    if os.path.exists(condition_file):
        with open(condition_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['PATIENT']
                condition_code = row.get('CODE', 'UNKNOWN')  # Use condition code (e.g., SNOMED/ICD10)
                condition_name = f"Condition_{condition_code}"
                if patient_id in patient_ids:
                    if not graph.has_node(condition_name):
                        graph.add_node(condition_name, type='condition', data=row)
                    graph.add_edge(patient_ids[patient_id], condition_name)

    # Read medications
    if os.path.exists(medication_file):
        with open(medication_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient_id = row['PATIENT']
                medication_code = row.get('CODE', 'UNKNOWN')  # Use medication code (e.g., RxNorm)
                medication_desc = row.get('DESCRIPTION', 'UnknownMedication')
                medication_name = f"Medication_{medication_code}_{medication_desc.replace(' ', '_')}"
                if patient_id in patient_ids:
                    if not graph.has_node(medication_name):
                        graph.add_node(medication_name, type='medication', data=row)
                    graph.add_edge(patient_ids[patient_id], medication_name)

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
    pipeline_pydantic(encoded_graph, "Incident", "MATCH (n) RETURN DISTINCT labels(n) AS NodeLabels")
    #pipeline(encoded_graph, "Incident", "MATCH (p:Person)-[:SCORED_GOAL]->(m:Match) RETURN m, collect(p) AS Players")
