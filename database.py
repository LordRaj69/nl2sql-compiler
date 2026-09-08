import os

import mysql.connector

from schema import SCHEMA


class DatabaseConnection:
    """Manages the MySQL 8 database used to execute generated SQL."""

    def __init__(self):
        self.config = {
            "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DATABASE", "nl2sql"),
        }

    def initialize(self):
        """Create tables described by the compiler schema if needed."""
        with mysql.connector.connect(**self.config) as connection:
            cursor = connection.cursor()
            for table_name, columns in SCHEMA.items():
                column_definitions = ", ".join(
                    f"{column_name} {self._mysql_type(column_type)}"
                    for column_name, column_type in columns.items()
                )
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} "
                    f"({column_definitions})"
                )
            cursor.close()

    def execute(self, sql):
        """Execute generated SQL and return column names and result rows."""
        with mysql.connector.connect(**self.config) as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            columns = [description[0] for description in cursor.description or []]
            rows = cursor.fetchall()
            cursor.close()
            return columns, rows

    @staticmethod
    def _mysql_type(column_type):
        if column_type == "VARCHAR":
            return "VARCHAR(255)"
        return column_type