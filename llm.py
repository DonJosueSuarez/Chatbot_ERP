import ollama
import json
from typing import Any
import database

async def human_query_to_sql(human_query: str) -> str | None:
    """Convierte una consulta en lenguaje natural a T-SQL usando un modelo local en Ollama."""
    
    database_schema = database.get_schema()

    system_message = f"""
    You are an AI that strictly translates natural language questions into T-SQL queries.
    Always return a valid JSON object with the key 'sql_query' containing the SQL query as a string.
    Do not include any reasoning or comments. Example output:
    {{
        "sql_query": "SELECT Cliente FROM cabecera_factura ORDER BY Total DESC LIMIT 1"
    }}
    If your response is not a valid JSON object, it will be considered incorrect.
    <schema>
    {database_schema}
    </schema>
    """

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_query}
        ],
        options={"temperature": 0}
    )
    
    print("Respuesta completa de Ollama:", response)

    # Verificar que la respuesta tiene el formato esperado
    content = response.get("message", {}).get("content", "")
    if not content:
        print("Error: Ollama devolvió una respuesta vacía o mal formada.")
        return None

    try:
        parsed_json = json.loads(content)  # Convertir la cadena JSON en un diccionario
        return parsed_json.get("sql_query")  # Extraer solo la consulta SQL
    except json.JSONDecodeError:
        print(f"Error al decodificar la respuesta de Ollama: {content}")
        return None

async def build_answer(result: list[dict[str, Any]], human_query: str) -> str | None:
    """Genera una respuesta en lenguaje natural basada en los resultados SQL."""
    
    system_message = """
    You are an AI that answers strictly based on provided SQL results.
    Return the SQL answer with a friendly language for the user.
    """

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"SQL Result: {result} \nUser Question: {human_query}"}
        ],
        options={"temperature": 0}
    )

    return response.get("message", {}).get("content", "")