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
    Do not add any commentary, explanations, or extra details—only return a valid JSON object with the key 'sql_query' containing the SQL query as a string. Do not include any reasoning or comments. Output example: {{"sql_query": "SELECT ..."}}
    If you output anything other than the JSON object, it will be considered an error.
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
        "max_tokens": 5000
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=payload, timeout=30)

    if response.status_code != 200:
        print(f"Error DeepSeek: {response.status_code} - {response.text}")
        return None

    print("Response from DeepSeek:", response.json())
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
        print(f"Error DeepSeek: {response.status_code} - {response.text}")
        return None

    return response.json()["choices"][0]["message"]["content"]
