import logging

from psycopg import Connection, Cursor
from services.getconf import Server
from app.objects import User

class QuerySender:

    def __init__(self):
        self.connection_str = Server.psql_url
        self.last_status = "0"

    def __base_query__(self, cursor: Cursor, query: str):
        print(f"Send query = '{query}'")
        cursor.execute(query)

    def __multi_query__(self, cursor: Cursor, query: str, params: list):
        ll_params = list([list([param]) for param in params])
        print(f"Send multiple query = '{query}' with arguments: {ll_params}")
        cursor.executemany(query, ll_params, returning=True)

    def send_query(self, query: str, return_result: bool, multi_query: bool = False, params: list = None):
          with Connection.connect(self.connection_str) as conn:
            print(f"DB Connected = {not conn.closed}")
            try:
                with conn.cursor() as crsr:
                    if multi_query:
                        if params == None or len(params) < 1: raise Exception("Некорректный ввод параметров мультизапроса")
                        else: result = self.__multi_query__(crsr, query, params)
                    else:
                        result = self.__base_query__(crsr, query)
                    conn.commit()
                    self.last_status = crsr.statusmessage
                    logging.info(f"Query success: {query}.\n\tSub-params: {params};\n\tStatus: {self.last_status}")
                    if return_result:
                        if multi_query and len(params) > 1:
                            result = []
                            while True:
                                result.append(crsr.fetchone())
                                if not crsr.nextset():
                                    break
                        else:
                            result = crsr.fetchall()
                        print(f"Result: {result}")
                        return result
            except BaseException as e: 
                conn.rollback() 
                logging.error(f'SQL-ошибка: "{e}"\n\tпри выполнении запроса: "{query}"\n\tДополнительные параметры запроса: {params}')                

class DataOperator(QuerySender):
    def __init__(self, table: str):
        super().__init__()
        self.table = table

    def get_records(self, out_columns: list[str] | None, condition: str | None = None, multi_query: bool = False, params: list = None):
        out_columns_str = '*'

        if out_columns != None and len(out_columns) > 0:
            out_columns_str = str(out_columns)[1:-1].replace("'", "")
        query_str = f"SELECT {out_columns_str} FROM {self.table}"

        if condition != None:
            query_str += f" WHERE {condition}"
        return super().send_query(query=query_str, return_result=True, multi_query=multi_query, params=params)

    def insert_records(self, in_columns: tuple[str], values: tuple[tuple[str]]) -> bool:
        if in_columns == None or len(in_columns) < 1: in_columns = ''
        else:
            in_columns_str = str(in_columns).replace("'", "")
        query_str = f"INSERT INTO {self.table} {in_columns_str} VALUES {values}"
        super().send_query(query_str, False)
        return self.last_status != None and self.last_status[-1] == '1'
    
    def delete_records(self, conditions: str) -> bool:
        query_str = f"DELETE FROM {self.table} WHERE {conditions}"
        super().send_query(query_str, False)
        return self.last_status != None and self.last_status[-1] == '1'
       
class UserOperator(DataOperator):
    def __init__(self, table: str, in_columns: tuple[str], out_columns: list[str], id_name: str = 'user_id'):
        super().__init__(table=table)
        self.in_columns = in_columns
        if id_name not in out_columns: out_columns.insert(0, id_name)
        self.out_columns = out_columns
        self.id_column = id_name
    
    def authorize(self, credential: str):
        result = super().get_records(self.out_columns, f"{self.id_column} = '{credential}'")
        if len(result) > 0:
            usr = result[0]
            usr_id = usr[0]
            usr_params = dict()
            for column, value in zip(self.out_columns[1:], usr[1:]):
                usr_params[column] = value
            return User(usr_id, usr_params)
        else: return None
    
    def add_user(self, user_id: str, name: str, role: str):
        return super().insert_records(self.in_columns, ((user_id, name, role)))
    
    def delete_users(self, id: str):
        return super().delete_records(f"{self.id_column} = '{id}'")
    
    def get_all_users(self):
        result = super().get_records(self.out_columns)
        users: list[User] = list()
        for usr in result:
            usr_params = dict()
            for column, value in zip(self.out_columns[1:], usr[1:]):
                usr_params[column] = value
            users.append(User(usr[0], usr_params))
        return users