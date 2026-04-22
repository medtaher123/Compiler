

class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value if self.value else self.children})"

class TerminalNode(ASTNode):
    def __init__(self, token):
        super().__init__(token.get_type_name(), value=token)

    def __repr__(self):
        return self.value.__repr__()

class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right):
        super().__init__('BinOp', [left, right], operator)

class DeclarationNode(ASTNode):
    def __init__(self, variable, value):
        super().__init__('Decl', [type, variable])

class TypeNode(ASTNode):
    def __init__(self, type_name):
        super().__init__('Type', value=type_name)

class AssignNode(ASTNode):
    def __init__(self, variable, value):
        super().__init__('Asign', [variable, value])

