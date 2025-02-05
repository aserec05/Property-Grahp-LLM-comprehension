from typing import Optional, List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from models import QueryResponse
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.2")

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
        return parsed_response

    except Exception as e:
        print(f"Error during model invocation or response parsing: {e}")


def pipeline_NL_to_query(graph, format_graph, query):
    """
    pipeline that get a query in natural langage and ask the query for this to the llm
    """
    system_template = "You are a graph expert. Here is a graph schema in the {format} format : {graph}. \
        Answer with ONE and only ONE query in Cypher. Don't say anything except the query."

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{query}")]
    )
    prompt = prompt_template.invoke({
        "format": format_graph,
        "graph": graph,
        "query": query
    })

    prompt.to_messages()
    response = model.invoke(prompt)
    print(response.content)
    return response.content


def pipeline(graph, format_graph, query):
    """Simple pipeline to interact with the LLM"""
    system_template = "Here is a graph in the {format} format : {graph}."
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{query}")])
    prompt = prompt_template.invoke({
        "format": format_graph,
        "graph": graph,
        "query": query
    })
    prompt.to_messages()
    response = model.invoke(prompt)
    print(response.usage_metadata)
    print(response.content)
    return response.content

def pipeline_NL_to_res(graph, format_graph, query):
    system_template = "You are a graph expert. Here is a graph in the {format} format : {graph}.\
        Give the answers of the natural langages questions."
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
        return parsed_response

    except Exception as e:
        print(f"Error during model invocation or response parsing: {e}")