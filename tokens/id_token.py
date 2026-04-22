from tokens.token import Token


class IdentifierToken(Token):
    PATTERN = r'[A-Za-z_][A-Za-z0-9_]*'

    def __repr__(self):
        return f"ID('{self.value}')"
