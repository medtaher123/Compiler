from os import terminal_size

from src.parser.grammar_analyser import EOF
from src.parser.nodes.ast_node import ASTNode, TerminalNode
from src.parser.nodes.actions import BuildBinOp, BuildAssign, BuildDecl, SemanticAction
from src.lexer.tokens.id_token import IdentifierToken
from src.lexer.tokens.number_token import NumberToken
from src.lexer.tokens.operator_token import OperatorToken
from src.lexer.tokens.pubctuation_token import PunctuationToken
from src.lexer.tokens.string_token import StringToken
from src.lexer.tokens.type_token import TypeToken

TOKEN_MAPPING = {
    '<id>': IdentifierToken,
    '<num>': NumberToken,
    '<type>': TypeToken,
    '<string>': StringToken,
    #'if': KeywordToken,  # You might need to check the .value == 'if' too. to be dealt with later on
    '+': OperatorToken,
    '=': OperatorToken,
    ';': PunctuationToken,
    '$': None            # Special case for End of File
}

terminal_symbols = {'<id>', '<num>', '<type>', '<str>', '+', '=', ';'}



class TableDrivenParser:
    def __init__(self, tokens, parsing_table, start_symbol):
        self.tokens = tokens + [None]  # Add EOF
        self.pos = 0
        self.table = parsing_table

        self.parse_stack = [EOF, start_symbol]
        self.semantic_stack = []
        self.step = 1

    def get_token_type_name(self, token):
        if token is None: return '$'
        return token.get_type_name()

    def format_stack0(self, stack):
        """Helper to format stacks nicely for the console."""
        if not stack: return "Empty"
        # For the parse stack, we want to see the top on the RIGHT
        # For the semantic stack, we'll just print the types of the nodes
        if len(stack) == 0 or isinstance(stack[0], str):
            return " ".join(stack)
        else:
            return " ".join(node.type for node in stack)

    def format_stack(self, stack, top_is_left=False):
        """Helper to format stacks nicely for the console."""
        if not stack: return "Empty"

        # If top_is_left is True, we reverse the list for display
        items = stack[::-1] if top_is_left else stack

        result = []
        for item in items:
            if hasattr(item, 'type'):  # If it's an ASTNode
                result.append(item.type)
            else:
                result.append(str(item))
        return " ".join(result)

    def get_remaining_input(self):
        """Gets the actual code values left to parse."""
        remaining = []
        for token in self.tokens[self.pos:]:
            if token is None:
                remaining.append('$')
            else:
                remaining.append(str(token.value))  # Print 'x', '5', '+', etc.
        return " ".join(remaining)

    def parse(self):
        print(
            f"\n{'STEP':<4} | {'PARSE STACK (Top Left)':<35} | {'REMAINING INPUT':<20} | {'SEMANTIC STACK':<20} | {'ACTION'}")
        print("-" * 125)

        while self.parse_stack:
            # 1. Capture current state for display
            # We set top_is_left=True for the Parse Stack!
            p_stack_str = self.format_stack(self.parse_stack, top_is_left=True)
            s_stack_str = self.format_stack(self.semantic_stack, top_is_left=False)
            remaining_str = self.get_remaining_input()

            current_token = self.tokens[self.pos]
            lookahead = self.get_token_type_name(current_token)

            # Pop the top of the stack
            top = self.parse_stack.pop()
            action_msg = ""

            # 2. Determine Action
            if top == lookahead:
                action_msg = f"Match '{top}'"
                if top in terminal_symbols:
                    self.semantic_stack.append(TerminalNode(token=current_token))
                self.pos += 1

            elif isinstance(top, SemanticAction):
                top.execute(self.semantic_stack)

            elif top in self.table:
                rule = self.table[top].get(lookahead)
                if rule is None:
                    # If we are looking for a statement and get something else
                    if top == "<stmt>":
                        raise SyntaxError(f"Syntax Error: Expected a declaration (int/str) or assignment, but found '{lookahead}'")
                    # Generic helpful message
                    raise SyntaxError(f"Syntax Error: Invalid '{lookahead}'. Was expecting tokens that form a {top}")
                action_msg = f"Apply {top} -> {' '.join(rule)}"
                self.push_rule_with_actions(top, rule)

            elif top == EOF:
                action_msg = "Accept! (Finished)"
                break
            else:
                if top == ';':
                    raise SyntaxError(f"Syntax Error: Missing semicolon ';' at the end of the line.")
                elif top == '=':
                    raise SyntaxError(f"Syntax Error: Expected '=' in assignment.")
                else:
                    raise SyntaxError(f"Syntax Error: Expected '{top}' but found '{lookahead}'")

            # 3. Print the step
            if len(p_stack_str) > 32: p_stack_str = p_stack_str[:29] + "..."
            if len(remaining_str) > 18: remaining_str = remaining_str[:15] + "..."
            if len(s_stack_str) > 18: s_stack_str = "..." + s_stack_str[-15:]

            print(f"{self.step:<4} | {p_stack_str:<35} | {remaining_str:<20} | {s_stack_str:<20} | {action_msg}")
            self.step += 1

        print("-" * 125)
        return self.semantic_stack

    def push_rule_with_actions(self, lhs, rule):
        if lhs == '<declaration>':
            self.parse_stack.append(BuildDecl())
        elif lhs == '<assignment>':
            self.parse_stack.append(BuildAssign())
        elif lhs == '<expr_prime>' and rule != ['epsilon']:
            self.parse_stack.append(BuildBinOp())

        # Push the standard grammar symbols
        if rule != ['epsilon']:
            for symbol in reversed(rule):
                self.parse_stack.append(symbol)

    def execute_action(self, action):
        if action == '#BUILD_DECL':
            var_id = self.semantic_stack.pop()  # The ID node
            self.semantic_stack.pop()
            var_type = self.semantic_stack.pop()  # The TYPE node
            self.semantic_stack.append(ASTNode('Decl', children=[var_type, var_id]))

        elif action == '#BUILD_ASSIGN':
            expr = self.semantic_stack.pop()
            self.semantic_stack.pop()
            var_id = self.semantic_stack.pop()
            self.semantic_stack.append(ASTNode('Assign', children=[var_id, expr]))

        elif action == '#BUILD_BINOP':
            right = self.semantic_stack.pop()
            operator = self.semantic_stack.pop()  # This should be the '+' operator node
            left = self.semantic_stack.pop()
            self.semantic_stack.append(ASTNode('BinOp', children=[left, right], value=operator))
