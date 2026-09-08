from lexer import tokenize
from parser import Parser
from semantic import SemanticAnalyzer
from codegen import SQLGenerator
from database import DatabaseConnection


def main():

    print("===================================")
    print("       Natural Language to SQL")
    print("===================================")

    query = input("\nEnter your query: ")

    try:
        # Phase 1: Lexical Analysis
        tokens = tokenize(query)

        print("\nTokens:")
        print(tokens)

        # Phase 2: Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()

        print("\nAST:")
        print(ast)

        # Phase 3: Semantic Analysis
        semantic = SemanticAnalyzer(ast)

        if not semantic.analyze():
            print("\nSemantic Errors:")
            for error in semantic.get_errors():
                print("-", error)
            return

        print("\nSemantic Analysis: Valid")

        # Phase 4: Code Generation
        generator = SQLGenerator(ast)
        sql = generator.generate()

        print("\nGenerated SQL:")
        print(sql)

        database = DatabaseConnection()
        database.initialize()
        columns, rows = database.execute(sql)

        print("\nQuery Results:")
        if not rows:
            print("No rows found.")
        else:
            print(" | ".join(columns))
            for row in rows:
                print(" | ".join(str(value) for value in row))

    except SyntaxError as error:
        print("\nSyntax Error:", error)

    except Exception as error:
        print("\nError:", error)


if __name__ == "__main__":
    main()