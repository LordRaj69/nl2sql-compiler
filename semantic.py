from schema import SCHEMA


class SemanticAnalyzer:

    def __init__(self, ast):
        self.ast = ast
        self.errors = []

    def analyze(self):
        table = self.get_table()

        if table not in SCHEMA:
            self.errors.append(
                f"Table '{table}' does not exist."
            )
            return False

        self.check_conditions(table)

        return len(self.errors) == 0

    def get_table(self):
        for child in self.ast.children:
            if child.node_type == "TABLE":
                return child.value

        return None

    def check_conditions(self, table):

        for child in self.ast.children:

            if child.node_type != "WHERE":
                continue

            for condition in child.children:

                if condition.node_type != "CONDITION":
                    continue

                column = condition.children[0].value
                value = condition.children[2].value

                # Check column exists
                if column not in SCHEMA[table]:
                    self.errors.append(
                        f"Column '{column}' does not exist."
                    )
                    continue

                column_type = SCHEMA[table][column]

                # Type checking
                if column_type == "INT":
                    try:
                        int(value)
                    except ValueError:
                        self.errors.append(
                            f"Column '{column}' expects an integer."
                        )

    def get_errors(self):
        return self.errors