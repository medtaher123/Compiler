from src.parser.nodes.ast_node import DeclarationNode, BinaryOpNode, AssignNode


class SemanticAction:
    """Base class for all semantic stack actions."""
    def execute(self, semantic_stack):
        raise NotImplementedError("Subclasses must implement execute()")
    def __repr__(self):
        return f"#{self.__class__.__name__}"

class BuildDecl(SemanticAction):
    def execute(self, stack):
        stack.pop()          # Discard the ';'
        var_id = stack.pop()
        var_type = stack.pop()
        stack.append(DeclarationNode(var_type, var_id))

class BuildAssign(SemanticAction):
    def execute(self, stack):
        stack.pop() # Discard the ';'
        expr = stack.pop()
        stack.pop()          # Discard the '='
        var_id = stack.pop()
        stack.append(AssignNode(var_id, expr))

class BuildBinOp(SemanticAction):
    def execute(self, stack):
        right = stack.pop()
        operator = stack.pop() # The '+' operator node
        left = stack.pop()
        stack.append(BinaryOpNode(operator, left, right))

