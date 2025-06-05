import json
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv
import database
import llm

app = FastAPI()

class PostHumanQueryPayload(BaseModel):
    human_query: str
    
class PostHumanQueryResponse(BaseModel):
    result: list
    
def limpiar_cadena(cadena: str) -> str:
    """
    Elimina caracteres de nueva línea, tabulaciones y retornos de carro de una cadena.
    """
    return cadena.replace('\n', '').replace('\r', '').replace('\t', '')


@app.post(
    "/human_query",
    name="Human Query",
    operation_id="post_human_query",
    description="""Gets a natural language query, internally transforms it to a SQL query, queries the database, and returns the result.""",)
async def human_query(payload: PostHumanQueryPayload) -> dict[str, str]:
    #transform human query to sql query
    sql_query = await llm.human_query_to_sql(payload.human_query)
    sql_query = limpiar_cadena(sql_query)
    if not sql_query:
        return{"error": "failed to generate SQL query"}
    result_dict = json.loads(sql_query)
    
    result = await database.query(result_dict["sql_query"])
    #return {"result": result}
    
    answer = await llm.build_answer(result, payload.human_query)
    if not answer:
        return{"error": "Failed to generate answer"}
    
    return{"answer": answer}