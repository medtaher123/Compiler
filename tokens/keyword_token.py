from tokens.token import Token


class KeywordToken(Token):
    # \b ensures we match whole words only (so 'if' matches, but 'iffy' does not)
    PATTERN = r'\b(?:if|then|else)\b'

    def __repr__(self):
        return f"KW('{self.value}')"
