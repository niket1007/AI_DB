import sqlite3
import os

class DBService:
    def __init__(self):
        self.conn = self.create_connection()

    def create_connection(self) -> sqlite3.Connection|None:
        try:
            path = os.path.join("users_database.sqlite")
            conn = sqlite3.connect(path)
            return conn
        except Exception as e:
            print(e)
            return None
    
    def create_user(self, username, password) -> bool|list[bool, str]:
        try:
            if(not self.check_username_exists(username)):
                create_query = f'INSERT INTO Users (username, password) VALUES("{username}", "{password}")'
                cursor = self.conn.cursor()
                cursor.execute(create_query)
                self.conn.commit()
                return True
            else:
                return [False, "Username already exists."]
        except Exception as e:
            print(e)
            return [False, str(e)]
    
    def check_username_exists(self, username: str) -> bool:
        try:
            select_query = f'SELECT username FROM Users WHERE username="{username}"'
            cursor = self.conn.cursor()
            res = cursor.execute(select_query)
            data = res.fetchone()
            if data is None:
                return False
            return True
        except Exception as e:
            print(e)
            return True

    def check_password(self, password_wriiten: str, username_written: str) -> list[bool, str]:
        try:
            select_query = f'SELECT u_id FROM Users WHERE username="{username_written}" AND password="{password_wriiten}"'
            cursor = self.conn.cursor()
            res = cursor.execute(select_query)
            data = res.fetchone()
            if data is None:
                return [False, "Username or Password invalid."]
            return [True, data[0]]
        except Exception as e:
            return [False, str(e)]
    
    def create_connection_string(
            self, u_id: int, name: str, conn_string: str, schema: str) -> list[bool, str|int|None]:
        try:
            create_query = ('INSERT INTO User_Connections (u_id, name, conn_string, schema) ' + 
                            f'VALUES({u_id}, "{name}", "{conn_string}", \'{schema}\')')
            print(create_query)
            cursor = self.conn.cursor()
            cursor.execute(create_query)
            self.conn.commit()
            return [True, cursor.lastrowid]
        except Exception as e:
            print(e)
            return [False, str(e)]
    
    def fetch_connection_strings(self, u_id: int) -> list|None:
        try:
            create_query = ('SELECT uc_id, name, conn_string, schema FROM User_Connections ' + 
                            f'WHERE u_id={u_id}')
            cursor = self.conn.cursor()
            res = cursor.execute(create_query)
            data = res.fetchall()
            return data
        except Exception as e:
            print(e)
            return None

