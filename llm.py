import httpx
from typing import Any

import database

# API Key de Mistral AI
API_KEY = "uR1g9WwaMJRGLyS7Pi8uCfhg1jkl7Zre"

# URL de la API de Mistral
API_URL = "https://api.mistral.ai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def human_query_to_sql(human_query: str) -> str | None:
    """Convierte una consulta en lenguaje natural a T-SQL usando Mistral AI."""
    
    database_schema = database.get_schema()
    
    system_message = f"""
    You are an AI that strictly translates natural language questions into T-SQL queries.
    Do not add any commentary, explanations, or extra details—only return the requested SQL query.
    Output must be in JSON format with the key 'sql_query'.
    <schema>
    {database_schema}
    </schema>
    """

    payload = {
        "model": "open-mixtral-8x22b",  # Usa el modelo que prefieras en Mistral
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_query}
        ],
        "temperature": 0,  # Respuesta precisa, sin variabilidad
        "max_tokens": 512  # Asegura que la salida sea concisa
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload, timeout=30.0)
    
    if response.status_code != 200:
        return None
    
    return response.json()["choices"][0]["message"]["content"]  # Devuelve solo la consulta SQL

async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """Genera una respuesta en lenguaje natural basada en los resultados SQL."""
    
    system_message = f"""
    You are an AI that answers strictly based on provided SQL results.
    Return sql answer with a friendly languaje per user.
    Answer in spanish
    """

    payload = {
        "model": "open-mixtral-8x22b",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"SQL Result: {result} \nUser Question: {human_query}"}
        ],
        "temperature": 0,
        "max_tokens": 500
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload, timeout=30.0)
    
    if response.status_code != 200:
        return None
    
    return response.json()["choices"][0]["message"]["content"]  # Devuelve solo la respuesta sin conversación

