from src.lexer.tokens.token import Token


class EOFToken(Token):
    PATTERN = r''  # No pattern needed, we create this token manually when we
    def __init__(self, line: int):
        super().__init__("$", line)