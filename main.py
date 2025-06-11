import json
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
import llm
import uvicorn
import re


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostHumanQueryPayload(BaseModel):
    human_query: str
    
class PostHumanQueryResponse(BaseModel):
    result: list
    
def limpiar_json(cadena: str) -> str:
    if cadena.startswith("```json"):
        cadena = cadena[len("```json"):]
    if cadena.endswith("```"):
        cadena = cadena[:-len("```")]
    return limpiar_formato_texto(cadena.strip())

def limpiar_formato_texto(cadena: str) -> str:
    """Elimina caracteres de formato como \n, \t y espacios innecesarios"""
    return re.sub(r"\s+", " ", cadena).strip()

    
@app.post(
    "/human_query",
    name="Human Query",
    operation_id="post_human_query",
    description="""Gets a natural language query, internally transforms it to a SQL query, queries the database, and returns the result.""",)
async def human_query(payload: PostHumanQueryPayload) -> dict[str, str]:
    sql_query = await llm.human_query_to_sql(payload.human_query)
    # Ya no es necesario limpiar aquí, porque llm.py debe devolver solo el SQL
    print(f"SQL QUERY OBTENIDO: {sql_query!r}")
    sql_query = limpiar_json(sql_query)
    print(f"SQL QUERY LIMPIADO: {sql_query!r}")

    if not sql_query:return {"error": "failed to generate SQL query"}
    result_dict = json.loads(sql_query)
    result = await database.query(result_dict["sql_query"])
    #return {"result": result}
    
    answer = await llm.build_answer(result, payload.human_query)
    if not answer:
        return {"error": "Failed to generate answer"}
    # Si la respuesta es un string, retorna como string. Si es un dict, conviértelo a string.
    if not isinstance(answer, str):
        answer = str(answer)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)