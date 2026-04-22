from tokens.token import Token


class OperatorToken(Token):
    # Matches +, -, *, /, =, >
    # We escape the - so it isn't treated as a range
    PATTERN = r'[+\-*/=>]'

    # Inherits the default __repr__ to just print '+' or '='