class Token:
    """Base class for all tokens."""
    # Every subclass will override this with its specific regex
    PATTERN = r''

    def __init__(self, value: str, line: int):
        self.value = value
        self.line = line

    def __repr__(self):
        """Default string representation, overridden by subclasses if needed."""
        return f"'{self.value}'"

    def get_type_name(self):
        """Return the class name as the token type."""
        return self.value
