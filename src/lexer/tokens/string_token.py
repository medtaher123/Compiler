from src.lexer.tokens.token import Token


class StringToken(Token):
    PATTERN = r'"(?:[^"\\]|\\.)*"'

    def __repr__(self):
        return f'STR({self.value})'

    def get_type_name(self):
        return "<str>"