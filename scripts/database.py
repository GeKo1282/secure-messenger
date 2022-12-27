import sqlite3
from typing import Union


class Database:
    databases = {}

    def __init__(self, path: str, name: str):
        self.path: str = path
        self.name: str = name

        if name in self.databases:
            raise Exception(f"Database with name {name} already exists!")

        self.databases[name] = self

    @staticmethod
    def get_database_by_name(name: str) -> "Database":
        if name not in Database.databases:
            raise Exception(f"No database named {name}!")
        return Database.databases[name]

    def create_table(self, table: str, columns: dict, if_not_exist=True):
        with sqlite3.connect(self.path) as database:
            columns_str = ("".join([f"{val_name} {val_type}, " for val_name, val_type in columns.items()]))[:-2]
            database.execute(f"CREATE TABLE {'IF NOT EXISTS' if if_not_exist else ''} {table} ({columns_str})")

    def drop_table(self, table: str):
        with sqlite3.connect(self.path) as database:
            database.execute(f"DROP TABLE {table}")

    def add_column(self, table: str, column_name: str, column_definition: str):
        with sqlite3.connect(self.path) as database:
            database.execute(f"ALTER TABLE {table} ADD {column_name} {column_definition}")

    def insert(self, table: str, values: list):
        with sqlite3.connect(self.path) as database:
            val_str = ""
            val_dict = {}

            for i, value in enumerate(values):
                val_str += "("
                for name, content in value.items():
                    val_str += f":{name}{i}, "
                    val_dict[f"{name}{i}"] = content
                val_str = val_str[:-2] + "), "
            val_str = val_str[:-2]

            database.execute(f"INSERT INTO {table} VALUES {val_str}", val_dict)

    def delete(self, table: str, var_str: str, var_dict: dict):
        with sqlite3.connect(self.path) as database:
            database.execute(f"DELETE FROM {table} WHERE {var_str}", var_dict)

    def update(self, table: str, var_str: str, var_dict: dict, updated: dict):
        with sqlite3.connect(self.path) as database:
            set_str = ("".join([f"{var}=:set_{var}, " for var in updated.keys()]))[:-2]
            set_var_dict = var_dict
            for var, val in updated.items():
                set_var_dict[f"set_{var}"] = val
            database.execute(f"UPDATE {table} SET {set_str} WHERE {var_str}", set_var_dict)

    def fetch(self, table: str, var_str: str, var_dict: dict, columns: str = "*", fetchall: bool = True):
        with sqlite3.connect(self.path) as database:
            if fetchall:
                return database.execute(f"SELECT {columns} FROM {table} WHERE {var_str}", var_dict).fetchall()
            return database.execute(f"SELECT {columns} FROM {table} WHERE {var_str}", var_dict).fetchone()

    def check_if_exists(self, table: str, var_str: str, var_dict: dict):
        return bool(self.fetch(table, var_str, var_dict))


class NameException(Exception):
    def __init__(self, message="Invalid name!"):
        super().__init__(message)
