from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from src.semantics.symbol_table import SymbolTable, VariableType, SymbolInfo
from src.parser.nodes.ast_node import ASTNode, TerminalNode, DeclarationNode, AssignNode, BinaryOpNode


class SeverityLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class CompilerMessage:
    """Represents a compiler error, warning, or info message."""
    severity: SeverityLevel
    line: int
    column: int
    message: str
    code: str  # e.g., "E001", "W001"
    
    def __repr__(self):
        return f"[{self.code}] {self.severity.value}: {self.message} (Line {self.line}, Col {self.column})"


class SemanticAnalyzer:
    """
    Performs semantic analysis on the AST:
    - Type checking (variable assignments match declared types)
    - Scope checking (variables used before declaration)
    - Usage tracking (warns about unused variables)
    - Expression type inference
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.messages: List[CompilerMessage] = []
        self.error_count = 0
        self.warning_count = 0
    
    def analyze(self, ast: List[ASTNode]) -> Tuple[bool, List[CompilerMessage]]:
        """
        Analyze the AST and return (success, messages).
        success = True if no errors (warnings are OK).
        """
        self.messages = []
        self.error_count = 0
        self.warning_count = 0
        
        # First pass: collect all declarations
        for node in ast:
            if isinstance(node, DeclarationNode):
                self._process_declaration(node)
        
        # Second pass: check assignments and expressions
        for node in ast:
            if isinstance(node, AssignNode):
                self._process_assignment(node)
        
        # Third pass: generate warnings for unused variables
        self._generate_usage_warnings()
        
        return self.error_count == 0, self.messages
    
    def _process_declaration(self, node: DeclarationNode) -> None:
        """Process a variable declaration with robust token handling."""
        type_node = node.children[0]
        id_node = node.children[1]
        
        # Extract the actual lexeme/value from the Token object
        # We try .value, then .lexeme, then just converting to string
        token_obj = type_node.value
        if hasattr(token_obj, 'value'):
            type_str = str(token_obj.value)
        elif hasattr(token_obj, 'lexeme'):
            type_str = str(token_obj.lexeme)
        else:
            type_str = str(token_obj)
            
        var_type = self._parse_type(type_str)
        
        id_token = id_node.value
        var_name = str(id_token.value) if hasattr(id_token, 'value') else str(id_token)
        
        line = getattr(id_token, 'line', 0) if hasattr(id_token, 'line') else 0
        
        if not self.symbol_table.declare(var_name, var_type, line):
            self._add_error(
                line=line,
                column=0,
                message=f"Variable '{var_name}' already declared",
                code="E001"
            )
    def _process_assignment(self, node: AssignNode) -> None:
        """
        Process a variable assignment.
        E.g., 'x = 5;' or 's = "hello";'
        Checks that:
        1. Variable exists (is declared)
        2. Type of RHS matches type of variable
        """
        # node.children = [IdentifierNode, ExpressionNode]
        id_node = node.children[0]
        expr_node = node.children[1]
        
        # Extract variable name
        var_name = id_node.value.value if hasattr(id_node, 'value') else str(id_node)
        line = getattr(id_node.value, 'line', 0) if hasattr(id_node, 'value') else 0
        
        # Check if variable is declared
        symbol = self.symbol_table.lookup(var_name)
        if symbol is None:
            self._add_error(
                line=line,
                column=0,
                message=f"Variable '{var_name}' used before declaration",
                code="E002"
            )
            return
        
        # Mark as used and assigned
        self.symbol_table.mark_as_used(var_name)
        self.symbol_table.mark_as_assigned(var_name)
        
        # Infer expression type
        expr_type = self._infer_expression_type(expr_node)
        
        # Check type compatibility
        if expr_type != VariableType.UNKNOWN and symbol.var_type != expr_type:
            self._add_error(
                line=line,
                column=0,
                message=f"Type mismatch: '{var_name}' is {symbol.var_type.value} but assigned {expr_type.value}",
                code="E003"
            )
    
    def _infer_expression_type(self, node: ASTNode) -> VariableType:
        """
        Infer the type of an expression by analyzing the AST.
        Returns the inferred type or UNKNOWN if cannot determine.
        """
        if isinstance(node, TerminalNode):
            token = node.value
            if hasattr(token, 'get_type_name'):
                type_name = token.get_type_name()
                if type_name == '<num>':
                    return VariableType.INT
                elif type_name == '<str>':
                    return VariableType.STRING
                elif type_name == '<id>':
                    # Look up variable type
                    var_name = token.value
                    symbol = self.symbol_table.lookup(var_name)
                    if symbol:
                        self.symbol_table.mark_as_used(var_name)
                        return symbol.var_type
                    else:
                        return VariableType.UNKNOWN
            return VariableType.UNKNOWN
        
        elif isinstance(node, BinaryOpNode):
            # For binary operations, infer types of operands
            left_type = self._infer_expression_type(node.children[0])
            right_type = self._infer_expression_type(node.children[1])
            
            operator = node.value.value if hasattr(node.value, 'value') else str(node.value)
            
            # Addition is polymorphic: int+int=int, string+string=string
            if operator == '+':
                if left_type == right_type:
                    return left_type
                elif left_type != VariableType.UNKNOWN and right_type != VariableType.UNKNOWN:
                    # Type mismatch in binary operation
                    line = getattr(node.value, 'line', 0) if hasattr(node, 'value') else 0
                    self._add_error(
                        line=line,
                        column=0,
                        message=f"Incompatible types in binary operation: {left_type.value} + {right_type.value}",
                        code="E004"
                    )
                    return VariableType.UNKNOWN
                else:
                    # At least one side is unknown, return the non-unknown one
                    return left_type if left_type != VariableType.UNKNOWN else right_type
            
            return VariableType.UNKNOWN
        
        return VariableType.UNKNOWN
    
    def _parse_type(self, type_str: str) -> VariableType:
        """Convert a type string to VariableType enum (now handles objects)."""
        # Ensure we are working with a string
        s = str(type_str).lower()
        if 'int' in s:
            return VariableType.INT
        elif 'string' in s or 'str' in s:
            return VariableType.STRING
        return VariableType.UNKNOWN
    
    def _generate_usage_warnings(self) -> None:
        """Generate warnings for unused variables."""
        unused = self.symbol_table.get_unused_symbols()
        for var_name in unused:
            symbol = self.symbol_table.lookup(var_name)
            self._add_warning(
                line=symbol.line,
                column=symbol.column,
                message=f"Variable '{var_name}' declared but never used",
                code="W001"
            )
    
    def _add_error(self, line: int, column: int, message: str, code: str) -> None:
        """Add an error message."""
        msg = CompilerMessage(
            severity=SeverityLevel.ERROR,
            line=line,
            column=column,
            message=message,
            code=code
        )
        self.messages.append(msg)
        self.error_count += 1
    
    def _add_warning(self, line: int, column: int, message: str, code: str) -> None:
        """Add a warning message."""
        msg = CompilerMessage(
            severity=SeverityLevel.WARNING,
            line=line,
            column=column,
            message=message,
            code=code
        )
        self.messages.append(msg)
        self.warning_count += 1
    
    def get_symbol_table(self) -> SymbolTable:
        """Return the symbol table for inspection."""
        return self.symbol_table