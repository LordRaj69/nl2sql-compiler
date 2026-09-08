class SQLGenerator:

    def __init__(self, ast):
        self.ast = ast

    def generate(self):

        table = None
        columns = ["*"]
        conditions = []

        # Find table and WHERE
        for child in self.ast.children:

            if child.node_type == "TABLE":
                table = child.value

            elif child.node_type == "COLUMNS":
                columns = [column.value for column in child.children]

            elif child.node_type == "WHERE":
                conditions = child.children

        # Start SQL query
        sql = f"SELECT {', '.join(columns)} FROM {table}"

        # Add WHERE conditions
        if conditions:

            sql += " WHERE "

            parts = []

            for condition in conditions:

                if condition.node_type == "CONDITION":

                    column = condition.children[0].value
                    operator = condition.children[1].value
                    value = condition.children[2].value

                    # Add quotes around text
                    if not value.isdigit():
                        value = f"'{value}'"

                    parts.append(
                        f"{column} {operator} {value}"
                    )

                elif condition.node_type == "LOGIC":

                    parts.append(condition.value.upper())

            sql += " ".join(parts)

        return sql + ";"