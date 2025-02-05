from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class QueryResponse(BaseModel):
    """Pydantic model for structured output"""
    query: str
    result: List[Dict] = Field(
        ..., description="List of result dictionaries where each dictionary represents a record."
    )

