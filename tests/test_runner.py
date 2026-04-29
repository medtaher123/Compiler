"""
Complete compiler test runner.
Demonstrates the full pipeline: Lexer → Parser → Semantic Analyzer
"""

from src.lexer.lexer import Lexer
from src.parser.grammar_analyser import GrammarAnalyzer
from src.parser.recursive_descent_parser import TableDrivenParser
from src.semantics.semantic_analyzer import SemanticAnalyzer
from src.utils.error_reporter import CompilerErrorReporter
from tests.test_cases import VALID_TESTS, INVALID_TESTS, EDGE_CASES


def setup_grammar():
    """Setup the language grammar (reusable)."""
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


def compile_source(source_code, grammar_analyzer, verbose=False):
    """
    Compile source code through all phases.
    Returns (success: bool, ast: List[ASTNode], messages: List[CompilerMessage])
    """
    try:
        # Phase 1: Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if verbose:
            print(f"  Tokens: {len(tokens)} token(s)")
        
        # Phase 2: Syntax Analysis
        parser = TableDrivenParser(tokens, grammar_analyzer.parsing_table, "<program>")
        ast = parser.parse()
        
        if verbose:
            print(f"  AST: {len(ast)} node(s)")
        
        # Phase 3: Semantic Analysis
        semantic_analyzer = SemanticAnalyzer()
        success, messages = semantic_analyzer.analyze(ast)
        
        if verbose:
            print(f"  Semantic: {semantic_analyzer.error_count} error(s), {semantic_analyzer.warning_count} warning(s)")
        
        return success, ast, messages, semantic_analyzer
    
    except Exception as e:
        # Lexer or Parser error caught here
        print(f"\n  [SYNTAX/LEXICAL ERROR] {e}")
        return False, [], [], None


def run_test(name, source_code, grammar_analyzer, expected_success=True, verbose=True):
    """
    Run a single test and report results.
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Test: {name}")
        print(f"{'='*70}")
    
    success, ast, messages, sem_analyzer = compile_source(source_code, grammar_analyzer, verbose=verbose)
    
    # Report results
    reporter = CompilerErrorReporter(source_code)
    
    # --- REPORTING LOGIC FIX ---
    if not success and not messages:
        # We failed in Phase 1 or 2 (Lexer/Parser)
        if verbose:
            print(f"\n  ✗ Compilation failed during Syntax/Lexical analysis.\n")
    elif messages:
        # We reached Semantic Analysis and found issues
        reporter.report(messages)
    else:
        # Everything passed
        if verbose:
            print(f"\n  ✓ Compilation successful (no errors)\n")
    
    if sem_analyzer and verbose:
        reporter.print_symbol_table(sem_analyzer.get_symbol_table())
    
    
    if expected_success is None:
        # Interactive mode
        status = "✓ DONE" 
        expected_str = "N/A (Interactive)"
    else:
        # Automated test suite mode
        status = "✓ PASS" if (success == expected_success) else "✗ FAIL"
        expected_str = "succeed" if expected_success else "fail"
    
    actual_str = "succeeded" if success else "failed"
    
    if verbose:
        print(f"  Expected: {expected_str}")
        print(f"  Actual: {actual_str}")
        print(f"  {status}\n")
    
    return success == expected_success if expected_success is not None else True


def run_test_suite(show_invalid=False, show_edge_cases=False):
    """
    Run the full test suite.
    """
    print("\n" + "="*70)
    print("COMPILER TEST SUITE")
    print("="*70)
    
    grammar = setup_grammar()
    
    all_passed = 0
    all_failed = 0
    
    # Valid tests
    print("\n" + "-"*70)
    print("VALID TESTS (Should compile successfully)")
    print("-"*70)
    
    for test_name, test_code in VALID_TESTS.items():
        passed = run_test(test_name, test_code, grammar, expected_success=True, verbose=False)
        if passed:
            print(f"  ✓ {test_name}")
            all_passed += 1
        else:
            print(f"  ✗ {test_name} (UNEXPECTED FAILURE)")
            all_failed += 1
    
    # Invalid tests
    if show_invalid:
        print("\n" + "-"*70)
        print("INVALID TESTS (Should fail compilation)")
        print("-"*70)
        
        for test_name, test_code in INVALID_TESTS.items():
            passed = run_test(test_name, test_code, grammar, expected_success=False, verbose=False)
            if passed:
                print(f"  ✓ {test_name}")
                all_passed += 1
            else:
                print(f"  ✗ {test_name} (UNEXPECTED PASS)")
                all_failed += 1
    
    # Edge cases
    if show_edge_cases:
        print("\n" + "-"*70)
        print("EDGE CASES (Mixed behavior)")
        print("-"*70)
        
        for test_name, test_code in EDGE_CASES.items():
            passed = run_test(test_name, test_code, grammar, expected_success=True, verbose=False)
            if passed:
                print(f"  ✓ {test_name}")
                all_passed += 1
            else:
                print(f"  ✗ {test_name}")
                all_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {all_passed} passed, {all_failed} failed")
    print("="*70 + "\n")
    
    return all_failed == 0


def interactive_mode():
    """
    Interactive mode: compile user-provided code.
    """
    grammar = setup_grammar()
    
    print("\n" + "="*70)
    print("INTERACTIVE COMPILER")
    print("="*70)
    print("Enter your source code (type 'END' on a new line to finish):")
    print()
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    source_code = "\n".join(lines)
    run_test("User Input", source_code, grammar, expected_success=None, verbose=True)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            run_test_suite(show_invalid=True, show_edge_cases=True)
        elif sys.argv[1] == "invalid":
            print("\n" + "="*70)
            print("DEMONSTRATING ERROR DETECTION")
            print("="*70)
            grammar = setup_grammar()
            for test_name, test_code in list(INVALID_TESTS.items())[:3]:
                run_test(test_name, test_code, grammar, expected_success=False, verbose=True)
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python test_runner.py [all|invalid|interactive]")
    else:
        run_test_suite(show_invalid=False, show_edge_cases=True)