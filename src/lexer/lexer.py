import re

from src.lexer.tokens.EOFToken import EOFToken
from src.lexer.tokens.id_token import IdentifierToken
from src.lexer.tokens.keyword_token import KeywordToken
from src.lexer.tokens.number_token import NumberToken
from src.lexer.tokens.operator_token import OperatorToken
from src.lexer.tokens.pubctuation_token import WhitespaceToken, PunctuationToken
from src.lexer.tokens.string_token import StringToken
from src.lexer.tokens.type_token import TypeToken


class Lexer:
    # The order here is CRITICAL.
    # KeywordToken MUST be evaluated before IdentifierToken, otherwise 'if' becomes an ID!
    TOKEN_CLASSES = [
        WhitespaceToken,
        KeywordToken,
        TypeToken,
        StringToken,
        IdentifierToken,
        NumberToken,
        OperatorToken,
        PunctuationToken
    ]

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.line = 1

    def tokenize(self):
        tokens = []
        position = 0
        code_length = len(self.source_code)

        while position < code_length:
            match = None

            # Try to match the current string against each token class
            for TokenClass in self.TOKEN_CLASSES:
                # re.match automatically checks only from the beginning of the string we pass it
                regex = re.compile(TokenClass.PATTERN)
                match = regex.match(self.source_code[position:])

                if match:
                    value = match.group(0)

                    # Keep track of line numbers for error reporting later
                    if '\n' in value:
                        self.line += value.count('\n')

                    # If it's not whitespace, instantiate the object and add it to our list
                    if TokenClass is not WhitespaceToken:
                        tokens.append(TokenClass(value, self.line))

                    # Advance our position in the source code
                    position += len(value)
                    break  # Stop checking other token classes for this position

            if not match:
                # If no class matched, we hit an invalid character
                illegal_char = self.source_code[position]
                raise SyntaxError(f"Illegal character '{illegal_char}' at line {self.line}")

        return tokens + [EOFToken(self.line)]  # Append EOF token at the end


# --- Testing ---
if __name__ == "__main__":
    code = """
    x=5+2;
    if a=b then a=a+1;
    int b;
    b="123";
    """
    lexer = Lexer(code)
    try:
        print(lexer.tokenize())
    except SyntaxError as e:
        print(e)