from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Set


class VariableType(Enum):
    INT = "int"
    STRING = "string"
    UNKNOWN = "unknown"


@dataclass
class SymbolInfo:
    """Information about a symbol (variable) in the symbol table."""
    name: str
    var_type: VariableType
    line: int
    column: int
    is_used: bool = False
    is_assigned: bool = False
    
    def __repr__(self):
        return f"Symbol({self.name}: {self.var_type.value}, declared at line {self.line})"


class SymbolTable:
    """
    Manages variable declarations and type information.
    Supports scope checking and usage tracking.
    """
    
    def __init__(self):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.scope_stack = [{}]  # Stack of scopes
        self.current_scope = 0
    
    def declare(self, name: str, var_type: VariableType, line: int, column: int = 0) -> bool:
        """
        Declare a new variable in the current scope.
        Returns True if successful, False if already declared.
        """
        if name in self.symbols:
            return False
        
        symbol = SymbolInfo(name, var_type, line, column)
        self.symbols[name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Look up a symbol by name.
        Returns SymbolInfo if found, None otherwise.
        """
        return self.symbols.get(name)
    
    def mark_as_used(self, name: str) -> bool:
        """
        Mark a variable as used (referenced in an expression).
        Returns True if successful, False if not found.
        """
        if name in self.symbols:
            self.symbols[name].is_used = True
            return True
        return False
    
    def mark_as_assigned(self, name: str) -> bool:
        """
        Mark a variable as assigned a value.
        Returns True if successful, False if not found.
        """
        if name in self.symbols:
            self.symbols[name].is_assigned = True
            return True
        return False
    
    def get_all_symbols(self) -> Dict[str, SymbolInfo]:
        """Return all declared symbols."""
        return self.symbols.copy()
    
    def get_unused_symbols(self) -> Set[str]:
        """Return names of variables declared but never used."""
        return {name for name, info in self.symbols.items() if not info.is_used}
    
    def get_unassigned_symbols(self) -> Set[str]:
        """Return names of variables declared but never assigned."""
        return {name for name, info in self.symbols.items() if not info.is_assigned}