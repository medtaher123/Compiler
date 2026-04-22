from tokens.token import Token


class NumberToken(Token):
    PATTERN = r'\d+'

    def __repr__(self):
        return f"NUM({self.value})"