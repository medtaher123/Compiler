import sys
import os
from src.lexer.lexer import Lexer
from src.parser.grammar_analyser import GrammarAnalyzer
from src.parser.parser import TableDrivenParser
from src.semantics.semantic_analyzer import SemanticAnalyzer
from src.utils.error_reporter import CompilerErrorReporter

def compile_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        source_code = f.read()

    # 1. Setup Grammar
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

    print(f"\n--- Compiling: {file_path} ---")

    try:
        # Phase 1: Lexer
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # Phase 2: Parser
        parser = TableDrivenParser(tokens, analyzer.parsing_table, "<program>")
        ast = parser.parse()

        # Phase 3: Semantic Analysis
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)

        # Output Results
        reporter = CompilerErrorReporter(source_code)
        reporter.report(messages)
        
        if success:
            reporter.print_symbol_table(semantic.get_symbol_table())
            print("Successfully compiled to AST and validated semantics.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sample_path = "samples/example_valid.txt"
        if os.path.exists(sample_path):
            compile_file(sample_path)
        else:
            print("Usage: python main.py <source_file>")
    else:
        compile_file(sys.argv[1])