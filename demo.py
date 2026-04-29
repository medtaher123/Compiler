"""
COMPILER PROJECT - QUICK START GUIDE

This script demonstrates the complete compiler pipeline.
Run it to see: Lexing → Parsing → Semantic Analysis → Error Reporting
"""

from src.lexer.lexer import Lexer
from src.parser.grammar_analyser import GrammarAnalyzer
from src.parser.recursive_descent_parser import TableDrivenParser
from src.semantics.semantic_analyzer import SemanticAnalyzer
from src.utils.error_reporter import CompilerErrorReporter

# Color codes for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def setup_grammar():
    """Initialize the language grammar."""
    grammar_text = """
    <program> ::= <stmt_list>
    <stmt_list> ::= <stmt> <stmt_list> | epsilon
    <stmt> ::= <declaration> | <assignment>
    <declaration> ::= <type> <id> ;
    <assignment> ::= <id> = <expr> ;
    <expr> ::= <term> <expr_prime>
    <expr_prime> ::= + <term> <expr_prime> | epsilon
    <term> ::= <id> | <num> | <str>
    """
    analyzer = GrammarAnalyzer()
    analyzer.load_from_string(grammar_text)
    analyzer.compute_first()
    analyzer.compute_follow()
    analyzer.build_parsing_table()
    return analyzer

def demo_valid_code():
    """Demonstrate compilation of valid code."""
    print_header("DEMO 1: Valid Code Compiles Successfully")
    
    source = """
    int x;
    int y;
    x = 10;
    y = 20;
    int sum;
    sum = x + y;
    """
    
    print("Source Code:")
    print(source)
    
    grammar = setup_grammar()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        reporter = CompilerErrorReporter(source)
        reporter.report(messages)
        reporter.print_symbol_table(semantic.get_symbol_table())
        
        if success:
            print(f"{GREEN}✓ COMPILATION SUCCESSFUL{RESET}\n")
    
    except Exception as e:
        print(f"Error: {e}\n")

def demo_type_error():
    """Demonstrate type checking error."""
    print_header("DEMO 2: Type Checking Detects Errors")
    
    source = """
    int x;
    x = "hello";
    """
    
    print("Source Code:")
    print(source)
    
    grammar = setup_grammar()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        reporter = CompilerErrorReporter(source)
        reporter.report(messages)
        
        if not success:
            print(f"Expected: Compilation should fail with type error\n")
    
    except Exception as e:
        print(f"Error: {e}\n")

def demo_undeclared_variable():
    """Demonstrate scope checking error."""
    print_header("DEMO 3: Scope Checking Detects Undeclared Variables")
    
    source = """
    y = 5;
    """
    
    print("Source Code:")
    print(source)
    
    grammar = setup_grammar()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        reporter = CompilerErrorReporter(source)
        reporter.report(messages)
        
        if not success:
            print(f"Expected: Variable 'y' used before declaration\n")
    
    except Exception as e:
        print(f"Error: {e}\n")

def demo_unused_variable_warning():
    """Demonstrate unused variable warning."""
    print_header("DEMO 4: Warnings for Unused Variables")
    
    source = """
    int x;
    int y;
    y = 10;
    """
    
    print("Source Code:")
    print(source)
    
    grammar = setup_grammar()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        reporter = CompilerErrorReporter(source)
        reporter.report(messages)
        reporter.print_symbol_table(semantic.get_symbol_table())
        
        print("Note: Code compiles (success=True) but with warnings\n")
    
    except Exception as e:
        print(f"Error: {e}\n")

def demo_string_concatenation():
    """Demonstrate string concatenation."""
    print_header("DEMO 5: String Concatenation")
    
    source = """
    string greeting;
    string name;
    string result;
    greeting = "hello";
    name = "world";
    result = greeting + name;
    """
    
    print("Source Code:")
    print(source)
    
    grammar = setup_grammar()
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        reporter = CompilerErrorReporter(source)
        reporter.report(messages)
        reporter.print_symbol_table(semantic.get_symbol_table())
        
        if success:
            print(f"{GREEN}✓ COMPILATION SUCCESSFUL{RESET}\n")
    
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}COMPILER PROJECT DEMONSTRATIONS{RESET}")
    print(f"{GREEN}Lexer → Parser → Semantic Analyzer{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    
    demo_valid_code()
    demo_type_error()
    demo_undeclared_variable()
    demo_unused_variable_warning()
    demo_string_concatenation()
    
    print(f"\n{GREEN}All demonstrations completed!{RESET}")
    print(f"Run: python -m tests.test_runner [all|invalid|interactive]\n")