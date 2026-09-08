from lexer import TokenType


class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"ASTNode({self.node_type}, {self.value}, {self.children})"


class Parser:
    IGNORED_WORDS = {"me", "the", "all", "records", "record", "data", "information", "of", "from", "with", "having", "is", "and"}
    CONDITION_WORDS = {"where", "whose", "having", "with"}

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

    def skip_words(self, words=None):
        words = words or self.IGNORED_WORDS
        while self.current_token() and self.current_token().value in words:
            self.consume()

    def parse(self):
        """
        Parses:
        show <table> [<column> ...] [where|whose <condition>]
        """

        # Expect a command such as show, list, find, or fetch.
        token = self.consume()

        if token.type != TokenType.KEYWORD or token.value != "show":
            raise SyntaxError("Query must start with show, list, find, get, or fetch")

        self.skip_words()

        # Accept both "show students name" and "show names from students".
        requested_columns = []
        while self.current_token() and self.current_token().type != TokenType.TABLE:
            if self.current_token().type == TokenType.COLUMN:
                requested_columns.append(ASTNode("COLUMN", self.consume().value))
            elif self.current_token().value in self.IGNORED_WORDS:
                self.consume()
            else:
                break

        token = self.current_token()

        if token is None or token.type != TokenType.TABLE:
            raise SyntaxError("Expected table name")

        # In phrases such as "student names from students", the first
        # table-like word describes the records and the table after "from"
        # is the actual source table.
        later_table = next(
            (
                index
                for index in range(self.position + 1, len(self.tokens))
                if self.tokens[index].type == TokenType.TABLE
                and any(
                    item.value == "from"
                    for item in self.tokens[self.position + 1:index]
                )
            ),
            None,
        )
        if later_table is not None:
            requested_columns.extend(
                ASTNode("COLUMN", item.value)
                for item in self.tokens[self.position + 1:later_table]
                if item.type == TokenType.COLUMN
            )
            self.position = later_table
            token = self.current_token()

        table_name = token.value
        self.consume()

        # SELECT node
        select_node = ASTNode(
            "SELECT",
            children=[
                ASTNode("TABLE", table_name)
            ]
        )

        # Optional column projection, for example: show students name
        columns = requested_columns
        token = self.current_token()
        while token and token.type == TokenType.COLUMN:
            columns.append(ASTNode("COLUMN", self.consume().value))
            token = self.current_token()

        self.skip_words(self.IGNORED_WORDS - self.CONDITION_WORDS)
        token = self.current_token()

        if columns:
            select_node.children.append(ASTNode("COLUMNS", children=columns))

        # Optional WHERE/WHOSE condition
        if token and token.type == TokenType.KEYWORD and token.value in self.CONDITION_WORDS:
            self.consume()

            where_node = self.parse_conditions()
            select_node.children.append(where_node)

        if self.current_token() is not None:
            raise SyntaxError(
                f"Unexpected word '{self.current_token().value}'"
            )

        return select_node

    def parse_conditions(self):
        """
        Parses:
        column operator value
        [and/or column operator value]
        """

        conditions = []

        while self.current_token():

            self.skip_words({"is"})
            column = self.consume()

            if column.type != TokenType.COLUMN:
                raise SyntaxError("Expected column name")

            if self.current_token() and self.current_token().value == "is":
                self.consume()
                if self.current_token() and self.current_token().type == TokenType.OPERATOR:
                    operator = self.consume()
                else:
                    operator = type(column)(TokenType.OPERATOR, "=")
            else:
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