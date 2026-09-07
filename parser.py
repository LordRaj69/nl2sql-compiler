from lexer import TokenType


class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"ASTNode({self.node_type}, {self.value}, {self.children})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def consume(self):
        token = self.current_token()
        self.position += 1
        return token

    def parse(self):
        """
        Parses:
        show <table> [where <condition>]
        """

        # Expect SHOW
        token = self.consume()

        if token.type != TokenType.KEYWORD or token.value != "show":
            raise SyntaxError("Query must start with 'show'")

        # Expect table
        token = self.consume()

        if token.type != TokenType.TABLE:
            raise SyntaxError("Expected table name")

        table_name = token.value

        # SELECT node
        select_node = ASTNode(
            "SELECT",
            children=[
                ASTNode("TABLE", table_name)
            ]
        )

        # Optional WHERE
        token = self.current_token()

        if token and token.type == TokenType.KEYWORD and token.value == "where":
            self.consume()

            where_node = self.parse_conditions()
            select_node.children.append(where_node)

        return select_node

    def parse_conditions(self):
        """
        Parses:
        column operator value
        [and/or column operator value]
        """

        conditions = []

        while self.current_token():

            column = self.consume()

            if column.type != TokenType.COLUMN:
                raise SyntaxError("Expected column name")

            operator = self.consume()

            if operator.type != TokenType.OPERATOR:
                raise SyntaxError("Expected operator")

            value = self.consume()

            if value.type not in (TokenType.NUMBER, TokenType.STRING):
                raise SyntaxError("Expected value")

            condition = ASTNode(
                "CONDITION",
                children=[
                    ASTNode("COLUMN", column.value),
                    ASTNode("OPERATOR", operator.value),
                    ASTNode("VALUE", value.value)
                ]
            )

            conditions.append(condition)

            # Check for AND / OR
            token = self.current_token()

            if not token:
                break

            if token.type == TokenType.KEYWORD and token.value in ("and", "or"):
                logic = self.consume()

                conditions.append(
                    ASTNode("LOGIC", logic.value)
                )
            else:
                break

        return ASTNode(
            "WHERE",
            children=conditions
        )