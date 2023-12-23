import sqlite3
from sqlite3 import Error


class DatabaseUtils:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_task_table()

    def create_connection(self):
        try:
            connection = sqlite3.connect(self.db_file)
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def execute_sql_query(self, query, *args, fetch_option = None):
        connection = self.create_connection()
        cursor = connection.cursor()
        if connection is not None:
            try:
                cursor.execute(query, *args)
                connection.commit()
                if fetch_option == "fetchone":
                    return cursor.fetchone()
                elif fetch_option == "fetchall":
                    return cursor.fetchall()
            except Error as e:
                print(f"Error: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            print("Cannot create the database connection.")

    def create_task_table(self):
        query = """CREATE TABLE IF NOT EXISTS tasks(
                   task_id INTEGER PRIMARY KEY,
                   task_title VARCHAR(255) NOT NULL,
                   date_the_task_was_added DATE DEFAULT CURRENT_TIMESTAMP,
                   description TEXT,
                   done BOOLEAN DEFAULT FALSE
                   );"""
        self.execute_sql_query(query)

    def add_task(self, task_title, description = None):
        query = "INSERT INTO tasks (task_title, description) VALUES (?, ?)"
        self.execute_sql_query(query, (task_title, description))

    def get_one_task(self, task_id):
        query = "SELECT * FROM tasks WHERE task_id = ?"
        task = self.execute_sql_query(query, (task_id, ), fetch_option = "fetchone")
        return task

    def get_all_tasks(self):
        query = "SELECT * FROM tasks"
        tasks = self.execute_sql_query(query, fetch_option = "fetchall")
        return tasks

    def update_task(self, task_id, task_title, description, done):
        query = "UPDATE tasks SET task_title = ?, description = ?, done = ? WHERE task_id = ?"
        self.execute_sql_query(query, (task_title, description, done, task_id))

    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE task_id = ?"
        self.execute_sql_query(query, (task_id, ))
