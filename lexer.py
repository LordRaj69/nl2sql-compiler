# lexer.py
import re
from schema import SCHEMA
from enum import Enum


class TokenType(Enum):
    KEYWORD = "KEYWORD"
    TABLE = "TABLE"
    COLUMN = "COLUMN"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    UNKNOWN = "UNKNOWN"

class Token:
    """
    Represents one token produced by the lexer.
    """

    def __init__(self, token_type, value):
        # Type of the token, such as KEYWORD or NUMBER
        self.type = token_type

        # Actual text/value found in the input
        self.value = value

    def __repr__(self):
        # Makes tokens easy to read while debugging
        return f"Token({self.type.name}, '{self.value}')"

# Natural-language keywords understood by our compiler.
# The dictionary maps each word to its corresponding token type.

KEYWORDS = {
    "show": TokenType.KEYWORD,
    "find": TokenType.KEYWORD,
    "get": TokenType.KEYWORD,
    "display": TokenType.KEYWORD,
    "where": TokenType.KEYWORD,
    "from": TokenType.KEYWORD,
    "all": TokenType.KEYWORD,
    "and": TokenType.KEYWORD,
    "or": TokenType.KEYWORD,
}

OPERATORS = {
    "greater": ">",
    "less": "<",
    "equal": "=",
    "not_equal": "!=",
    "greater_equal": ">=",
    "less_equal": "<=",
}

def identify_word(word):
    """
    Identifies whether a word is a keyword, table,
    column, or unknown word.
    """

    word = word.lower()

    # Check whether the word represents a comparison operator.
    if word in OPERATORS:
        return Token(TokenType.OPERATOR, OPERATORS[word])

    # Check whether the word is a number.
    if word.isdigit():
        return Token(TokenType.NUMBER, word)

    # First check natural-language keywords.
    if word in KEYWORDS:
        return Token(KEYWORDS[word], word)

    # Check whether the word is a table name.
    if word in SCHEMA:
        return Token(TokenType.TABLE, word)

    # Check whether the word is a column name.
    for columns in SCHEMA.values():
        if word in columns:
            return Token(TokenType.COLUMN, word)

    # Word is not recognized yet.
    return Token(TokenType.UNKNOWN, word)

MULTI_WORD_OPERATORS = {
    "greater than or equal to": ">=",
    "less than or equal to": "<=",
    "greater than": ">",
    "less than": "<",
    "equal to": "=",
    "not equal to": "!=",
}


def find_operator_phrase(text):
    """
    Checks whether the input contains a known
    multi-word comparison operator.

    Returns the SQL operator if found.
    """

    text = text.lower()

    # Check longer phrases first.
    # For example, "greater than or equal to"
    # must be checked before "greater than".
    for phrase, operator in MULTI_WORD_OPERATORS.items():
        if phrase in text:
            return operator

    return None



def tokenize(text):
    """
    Converts a complete natural-language query
    into a list of tokens.
    """

    text = text.lower()

    # Check longer operator phrases first.
    phrases = sorted(
        MULTI_WORD_OPERATORS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    # Replace multi-word operators with their symbols.
    for phrase, symbol in phrases:
        if phrase in text:
            text = text.replace(phrase, f" {symbol} ")

    # Keep quoted text together.
    # Example: "raj wardhan" remains one token.
    words = re.findall(r'"[^"]*"|\S+', text)

    tokens = []

    for word in words:

        # Remove quotation marks from string values.
        if word.startswith('"') and word.endswith('"'):
            tokens.append(Token(TokenType.STRING, word[1:-1]))

        # Recognize comparison operators.
        elif word in OPERATORS.values():
            tokens.append(Token(TokenType.OPERATOR, word))

        else:
            tokens.append(identify_word(word))

    return tokens