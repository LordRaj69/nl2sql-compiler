# schema.py
# Stores the database schema understood by our NL-to-SQL compiler.

SCHEMA = {
    "students": {
        "id": "INT",
        "name": "VARCHAR",
        "age": "INT",
        "department": "VARCHAR"
    }
}

def get_schema_keywords():
    """
    Returns all table names and column names.

    The lexer will later use these keywords
    when correcting misspelled words.
    """

    keywords = []

    # Add table names
    for table_name, columns in SCHEMA.items():
        keywords.append(table_name)

        # Add column names
        keywords.extend(columns.keys())

    return keywords