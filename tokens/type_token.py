from tokens.token import Token


class TypeToken(Token):
    PATTERN = r'\b(?:int|string)\b'

    def __repr__(self):
        return f"TYPE('{self.value}')"

    def get_type_name(self):
        return "<type>"