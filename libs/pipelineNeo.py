from typing import List, Dict
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from models import QueryResponse

class Neo4jPipeline:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def run_query(self, query: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def execute_queries_from_file(self, file_path: str) -> List[QueryResponse]:
        queries = self.load_queries(file_path)
        responses = []
        for query in queries:
            result = self.run_query(query)
            responses.append(QueryResponse(query=query, result=result))
        #result = self.run_query(queries[0])
        #responses.append(QueryResponse(query=queries[0], result=result))
        return responses

    @staticmethod
    def load_queries(file_path: str) -> List[str]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]

if __name__ == "__main__":
    NEO4J_URI = "bolt://localhost:7687"  # Modifier selon votre configuration
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"
    QUERIES_FILE = "requests/queries.txt"

    pipeline = Neo4jPipeline(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        responses = pipeline.execute_queries_from_file(QUERIES_FILE)
        for response in responses:
            print(response.model_dump_json(indent=2))
    finally:
        pipeline.close()
