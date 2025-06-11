import httpx
import ollama
import json
from typing import Any
import database

import re

async def human_query_to_sql(human_query: str) -> str | None:
    """Convierte una consulta en lenguaje natural a T-SQL usando sqlcoder."""
    
    database_schema = database.get_schema()

    system_message = f"""
    You are an AI that strictly translates natural language questions into T-SQL queries for Microsoft SQL Server.
    IMPORTANT:
    - Only use valid T-SQL syntax for SQL Server.
    - NEVER use LIMIT. ALWAYS use SELECT TOP n ...
    - If you use aggregate functions (SUM, COUNT, AVG, etc.), ALWAYS include a GROUP BY for the non-aggregated columns in the SELECT.
    - If the user asks for the client with the highest total, you must use GROUP BY Cliente and ORDER BY SUM(Total) DESC, and select SUM(Total) as TotalFacturado.
    - Example: SELECT TOP 1 Cliente, SUM(Total) as TotalFacturado FROM cabecera_factura GROUP BY Cliente ORDER BY TotalFacturado DESC
    - Do not add any commentary, explanations, or extra details—only return a valid JSON object.

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
                "model": "sqlcoder",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": human_query}
                ],
                "stream": False
            }
        )
        
    if response.status_code != 200:
        return None
    print(f"Response from Ollama: {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]

async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """Genera una respuesta en lenguaje natural basada en los resultados SQL."""

    system_message = """
    You are an AI that answers strictly based on provided SQL results.
    Return sql answer with a friendly languaje per user.
    """

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "temperature": 0,
                "model": "sqlcoder",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"SQL Result: {result} \nUser Question: {human_query}"}
                ],
                "stream": False
            }
        )
    
    if response.status_code != 200:
        return None
    return response.json()["choices"][0]["message"]["content"]