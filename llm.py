import httpx
import ollama
import json
from typing import Any
import database

import re

async def human_query_to_sql(human_query: str) -> str | None:
    """Convierte una consulta en lenguaje natural a T-SQL usando gemma2:2b local en Ollama."""
    
    database_schema = database.get_schema()
    
    system_message = f"""
    You are an AI that strictly translates natural language questions into T-SQL queries for Microsoft SQL Server.
    IMPORTANT: Only use valid T-SQL syntax for SQL Server. NEVER use LIMIT. ALWAYS use SELECT TOP n ...
    Do not add any commentary, explanations, or extra details—only return a valid JSON object.

    Always respond in JSON format as:
    {{"sql_query": "<your SQL query>"}}

    <schema>
    {database_schema}
    </schema>
    """

    user_message = human_query
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",  # Ajusta el puerto si es necesario
            json={
                "temperature": 0,
                "model": "gemma2:2b",
                "prompt": f"{system_message}\n\n{user_message}",
                "stream": False
            }
        )
        
    if response.status_code != 200:
        return None
    print(f"Response from Ollama: {response.text}")
    response_data = response.json()
    if "response" not in response_data:
        return None
    return response_data["response"]


async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """Genera una respuesta en lenguaje natural basada en los resultados SQL."""
    
    system_message = f"""
    You are an AI that answers strictly based on provided SQL results.
    Return sql answer with a friendly languaje per user in spanish language.
    SQL Results:
    {result}
    """

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "temperature": 0,
                "model": "gemma2:2b",
                "prompt": system_message,
                "stream": False
            }
        )
    
    if response.status_code != 200:
        return None
    
    return response.json()["response"]
