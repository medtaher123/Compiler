# Assuming your previous classes are imported or in the same file
from RecursiveDescentParser import TableDrivenParser
from grammar_analyser import GrammarAnalyzer
from lexer import Lexer  # Your Milestone 1 Lexer



def test_compiler():
    # 1. Define our Grammar
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
    analyzer.display_results()
    analyzer.build_parsing_table()
    analyzer.display_table_pretty()

    # 3. Input Source Code
    source_code = """
    int x;
    x = 5 + 2;
    a = b + 3;
    string s;
    s = "hello";
    """

    # 4. Run Lexer
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()  # Returns list of IdentifierToken, NumberToken, etc.

    # 5. Run Table-Driven Parser
    parser = TableDrivenParser(tokens, analyzer.parsing_table, "<program>")

    try:
        ast_root = parser.parse()
        print("\n" + "=" * 30)
        print("PARSING SUCCESSFUL")
        print("=" * 30)
        print(f"Final AST: {ast_root}")
    except Exception as e:
        print(f"Parsing Error: {e}")


if __name__ == "__main__":
    test_compiler()