from tokens.token import Token


class PunctuationToken(Token):
    PATTERN = r'[{}();]'

    # Inherits the default __repr__ to just print ';' or '{'


class WhitespaceToken(Token):
    PATTERN = r'[ \t\n]+'
    # We won't actually print these, but the Lexer needs to match them to skip them
