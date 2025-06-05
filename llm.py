import httpx
from typing import Any
import database

# URL y cabecera de la API de DeepSeek en OpenRouter
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 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"
}

async def human_query_to_sql(human_query: str) -> str | None:
    """Convierte una consulta en lenguaje natural a T-SQL usando Deepseek AI."""
    
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
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_query}
        ],
        "temperature": 0,
        "max_tokens": 512
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload, timeout=30)

    if response.status_code != 200:
        return None

    return response.json()["choices"][0]["message"]["content"]

async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """Genera una respuesta en lenguaje natural basada en los resultados SQL."""

    system_message = """
    You are an AI that answers strictly based on provided SQL results.
    Return sql answer with a friendly languaje per user.
    """

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"SQL Result: {result} \nUser Question: {human_query}"}
        ],
        "temperature": 0,
        "max_tokens": 600
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload, timeout=30)

    if response.status_code != 200:
        return None

    return response.json()["choices"][0]["message"]["content"]
