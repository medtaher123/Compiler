from grammar.grammar_parser import EOF, EPSILON
from tokens.id_token import IdentifierToken
from tokens.keyword_token import KeywordToken
from tokens.number_token import NumberToken
from tokens.operator_token import OperatorToken
from tokens.pubctuation_token import PunctuationToken

TOKEN_MAPPING = {
    'id': IdentifierToken,
    'num': NumberToken,
    'if': KeywordToken,  # You might need to check the .value == 'if' too
    '+': OperatorToken,
    '=': OperatorToken,
    ';': PunctuationToken,
    '$': None            # Special case for End of File
}



class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value if self.value else self.children})"


class TableDrivenParser:
    def __init__(self, tokens, parsing_table, start_symbol):
        self.tokens = tokens + [None]  # Add EOF
        self.pos = 0
        self.table = parsing_table

        self.parse_stack = [EOF, start_symbol]
        self.semantic_stack = []
        self.step = 1

    def get_token_type_name(self, token):
        if token is None: return EOF
        if type(token).__name__ == 'IdentifierToken': return 'id'
        if type(token).__name__ == 'NumberToken': return 'num'
        return token.value

    def format_stack(self, stack):
        """Helper to format stacks nicely for the console."""
        if not stack: return "Empty"
        # For the parse stack, we want to see the top on the RIGHT
        # For the semantic stack, we'll just print the types of the nodes
        if len(stack) == 0 or isinstance(stack[0], str):
            return " ".join(stack)
        else:
            return " ".join(node.type for node in stack)

    def parse(self):
        print(
            f"\n{'STEP':<5} | {'PARSE STACK (Top is Right)':<40} | {'LOOKAHEAD':<10} | {'SEMANTIC STACK':<25} | {'ACTION'}")
        print("-" * 120)

        while self.parse_stack:
            # 1. Capture current state for display
            p_stack_str = self.format_stack(self.parse_stack)
            s_stack_str = self.format_stack(self.semantic_stack)

            current_token = self.tokens[self.pos]
            lookahead = self.get_token_type_name(current_token)

            # Pop the top of the stack
            top = self.parse_stack.pop()
            action_msg = ""

            # 2. Determine Action
            if top == lookahead:
                action_msg = f"Match '{top}'"
                if top in ('id', 'num'):
                    self.semantic_stack.append(ASTNode(top, value=current_token.value))
                self.pos += 1

            elif str(top).startswith('#'):
                action_msg = f"Execute {top}"
                self.execute_action(top)

            elif top in self.table:
                rule = self.table[top].get(lookahead)
                if rule is None:
                    raise SyntaxError(f"Syntax Error: Unexpected '{lookahead}' while looking for '{top}'")

                action_msg = f"Apply {top} -> {' '.join(rule)}"
                self.push_rule_with_actions(top, rule)

            elif top == EOF:
                action_msg = "Accept! (Finished)"
                break
            else:
                raise SyntaxError(f"Error: Unknown symbol '{top}' on stack")

            # 3. Print the step
            # Truncate strings with [...] if they get too long for the console
            if len(p_stack_str) > 38: p_stack_str = "..." + p_stack_str[-35:]
            if len(s_stack_str) > 23: s_stack_str = "..." + s_stack_str[-20:]

            print(f"{self.step:<5} | {p_stack_str:<40} | {lookahead:<10} | {s_stack_str:<25} | {action_msg}")
            self.step += 1

        print("-" * 120)
        return self.semantic_stack.pop()

    def push_rule_with_actions(self, lhs, rule):
        if lhs == 'Stmt':
            self.parse_stack.append('#BUILD_ASSIGN')
        elif lhs == 'ExprPrime' and rule != ['epsilon']:
            self.parse_stack.append('#BUILD_BINOP')

        if rule != ['epsilon']:
            for symbol in reversed(rule):
                self.parse_stack.append(symbol)

    def execute_action(self, action):
        if action == '#BUILD_ASSIGN':
            expr = self.semantic_stack.pop()
            var_name = self.semantic_stack.pop()
            self.semantic_stack.append(ASTNode('Assign', children=[var_name, expr]))

        elif action == '#BUILD_BINOP':
            right = self.semantic_stack.pop()
            left = self.semantic_stack.pop()
            self.semantic_stack.append(ASTNode('BinOp', children=[left, right], value='+'))