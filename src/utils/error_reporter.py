from typing import List
from src.semantics.semantic_analyzer import CompilerMessage, SeverityLevel


class CompilerErrorReporter:
    """
    Professional compiler error reporter with:
    - Color-coded output (red for errors, yellow for warnings)
    - Source code line pointers with caret (^)
    - Summary statistics
    """
    
    # ANSI color codes
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self, source_code: str):
        """
        Initialize the reporter with source code.
        source_code: The original source code string.
        """
        self.source_code = source_code
        self.lines = source_code.split('\n')
    
    def report(self, messages: List[CompilerMessage]) -> None:
        """
        Print all messages with formatting and source pointers.
        """
        if not messages:
            print(f"\n{self.GREEN}✓ No errors or warnings!{self.RESET}\n")
            return
        
        print()  # Blank line before output
        
        # Sort by line number
        sorted_messages = sorted(messages, key=lambda m: (m.line, m.column))
        
        for msg in sorted_messages:
            self._print_message(msg)
        
        # Print summary
        self._print_summary(messages)
    
    def _print_message(self, msg: CompilerMessage) -> None:
        """Print a single message with source code pointer."""
        # Color based on severity
        if msg.severity == SeverityLevel.ERROR:
            color = self.RED
            icon = "✗"
        elif msg.severity == SeverityLevel.WARNING:
            color = self.YELLOW
            icon = "⚠"
        else:
            color = self.BLUE 
            icon = "ℹ"
        
        # Print header: [CODE] SEVERITY: message
        header = f"{color}{icon} [{msg.code}] {msg.severity.value}: {msg.message}{self.RESET}"
        print(header)
        
        # Print source line
        if 0 <= msg.line - 1 < len(self.lines):
            source_line = self.lines[msg.line - 1]
            print(f"  {self.CYAN}Line {msg.line}:{self.RESET} {source_line}")
            
            # Print pointer (caret)
            if msg.column > 0:
                pointer = " " * (msg.column - 1) + "^"
            else:
                # If no column info, point to start of line
                pointer = " " * (len(f"  Line {msg.line}: ") - 2) + "^"
            print(f"  {color}{pointer}{self.RESET}")
        
        print()  # Blank line after each message
    
    def _print_summary(self, messages: List[CompilerMessage]) -> None:
        """Print summary statistics."""
        errors = [m for m in messages if m.severity == SeverityLevel.ERROR]
        warnings = [m for m in messages if m.severity == SeverityLevel.WARNING]
        
        summary_parts = []
        
        if errors:
            summary_parts.append(f"{self.RED}{len(errors)} error{'s' if len(errors) > 1 else ''}{self.RESET}")
        
        if warnings:
            summary_parts.append(f"{self.YELLOW}{len(warnings)} warning{'s' if len(warnings) > 1 else ''}{self.RESET}")
        
        if summary_parts:
            summary = f"Compilation failed: {', '.join(summary_parts)}"
            print(f"{self.BOLD}{summary}{self.RESET}\n")
        else:
            print(f"{self.GREEN}{self.BOLD}Compilation successful!{self.RESET}\n")
    
    def print_symbol_table(self, symbol_table) -> None:
        """Pretty-print the symbol table."""
        symbols = symbol_table.get_all_symbols()
        
        if not symbols:
            print(f"{self.CYAN}Symbol Table: (empty){self.RESET}\n")
            return
        
        print(f"\n{self.BOLD}{self.CYAN}Symbol Table:{self.RESET}")
        print("-" * 70)
        print(f"{'Variable':<15} {'Type':<10} {'Line':<6} {'Used':<6} {'Assigned':<10}")
        print("-" * 70)
        
        for name, info in sorted(symbols.items()):
            used_str = "✓" if info.is_used else "✗"
            assigned_str = "✓" if info.is_assigned else "✗"
            print(f"{name:<15} {info.var_type.value:<10} {info.line:<6} {used_str:<6} {assigned_str:<10}")
        
        print("-" * 70)
        print()