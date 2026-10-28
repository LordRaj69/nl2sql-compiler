from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FilterCondition:
    column: str
    operator: str
    value: str
    logic: Optional[str] = None


@dataclass
class IntermediateQuery:
    table: str
    columns: List[str]
    conditions: List[FilterCondition]

    def format(self):
        lines = ["%1 = SCAN " + self.table]
        source = "%1"

        if self.conditions:
            parts = []
            for condition in self.conditions:
                if condition.logic:
                    parts.append(condition.logic.upper())
                value = condition.value
                if not value.isdigit():
                    value = f"'{value}'"
                parts.append(f"{condition.column} {condition.operator} {value}")

            lines.append(f"%2 = FILTER {' '.join(parts)} FROM {source}")
            source = "%2"

        result = "%3" if self.conditions else "%2"
        lines.append(
            f"{result} = PROJECT {', '.join(self.columns)} FROM {source}"
        )
        lines.append(f"RETURN {result}")
        return "\n".join(lines)


class IntermediateCodeGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self):
        table = None
        columns = ["*"]
        conditions = []
        pending_logic = None

        for child in self.ast.children:
            if child.node_type == "TABLE":
                table = child.value
            elif child.node_type == "COLUMNS":
                columns = [column.value for column in child.children]
            elif child.node_type == "WHERE":
                for item in child.children:
                    if item.node_type == "LOGIC":
                        pending_logic = item.value
                    elif item.node_type == "CONDITION":
                        conditions.append(
                            FilterCondition(
                                column=item.children[0].value,
                                operator=item.children[1].value,
                                value=item.children[2].value,
                                logic=pending_logic,
                            )
                        )
                        pending_logic = None

        if table is None:
            raise ValueError("Cannot generate intermediate code without a table.")

        return IntermediateQuery(table, columns, conditions)
