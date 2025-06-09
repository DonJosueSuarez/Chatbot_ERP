from typing import Any
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


username = 'sa'
password = '12345'
server = 'DESKTOP-2FDM7CO'
database = 'SONGPruebas'
engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
session = sessionmaker(bind=engine)

def get_schema() -> str:
   inspector = inspect(engine)
   table_names = inspector.get_view_names()
   
   def get_column_details(table_name) -> list[str]:
      columns = inspector.get_columns(table_name)
      return[f"{col['name']} ({col['type']})" for col in columns]
    
   schema_info = []
   for table_name in table_names:
      table_info = [f"Table: {table_name}"]
      table_info.append("Columns:")
      table_info.extend(f" - {column}" for column in get_column_details(table_name))
      schema_info.append("\n".join(table_info))
          
   engine.dispose() 
   print(schema_info)       
   return "\n\n".join(schema_info)

async def query(sql_query: str) -> list[dict[str, Any]]:
   print("sql_query", sql_query)
   try:
      with session() as sess:
         statement = text(sql_query)
         result = sess.execute(statement)
         return [dict(row._mapping) for row in result]
   except Exception as e:
      print(f"Error ejecutando la consulta: {e}")
      return []
   
def cleaup() -> None:
   engine.dispose()