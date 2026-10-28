class SQLGenerator:

    def __init__(self, intermediate):
        self.intermediate = intermediate

    def generate(self):
        sql = (
            f"SELECT {', '.join(self.intermediate.columns)} "
            f"FROM {self.intermediate.table}"
        )

        if self.intermediate.conditions:
            parts = []
            for condition in self.intermediate.conditions:
                if condition.logic:
                    parts.append(condition.logic.upper())

                value = condition.value
                if not value.isdigit():
                    value = f"'{value}'"
                parts.append(f"{condition.column} {condition.operator} {value}")

            sql += " WHERE " + " ".join(parts)

        return sql + ";"