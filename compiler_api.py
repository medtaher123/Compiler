"""
Compiler API Server (Flask)

Exposes the compiler pipeline as REST endpoints for the web UI.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lexer.lexer import Lexer
from src.parser.grammar_analyser import GrammarAnalyzer
from src.parser.recursive_descent_parser import TableDrivenParser
from src.semantics.semantic_analyzer import SemanticAnalyzer
from src.utils.error_reporter import CompilerErrorReporter

app = Flask(__name__)
CORS(app)

# Global grammar (setup once)
GRAMMAR = None

def setup_grammar():
    """Initialize the grammar."""
    global GRAMMAR
    if GRAMMAR is None:
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
        GRAMMAR = GrammarAnalyzer()
        GRAMMAR.load_from_string(grammar_text)
        GRAMMAR.compute_first()
        GRAMMAR.compute_follow()
        GRAMMAR.build_parsing_table()
    return GRAMMAR

@app.route('/api/compile', methods=['POST'])
def compile():
    """
    Compile source code.
    
    Request body:
    {
        "source": "int x; x = 5;"
    }
    
    Response:
    {
        "success": true,
        "messages": [...],
        "ast": [...],
        "symbolTable": {...},
        "tokens": [...]
    }
    """
    try:
        data = request.json
        source = data.get('source', '')
        
        if not source.strip():
            return jsonify({
                'success': False,
                'error': 'Source code cannot be empty',
                'messages': []
            }), 400
        
        grammar = setup_grammar()
        
        # Phase 1: Lexing
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        token_list = [
            {
                'value': str(token.value),
                'type': token.get_type_name(),
                'line': token.line
            }
            for token in tokens[:-1]  # Exclude EOF
        ]
        
        # Phase 2: Parsing
        parser = TableDrivenParser(tokens, grammar.parsing_table, "<program>")
        ast = parser.parse()
        
        # Phase 3: Semantic Analysis
        semantic = SemanticAnalyzer()
        success, messages = semantic.analyze(ast)
        
        # Convert messages to JSON
        message_list = [
            {
                'code': msg.code,
                'severity': msg.severity.value,
                'line': msg.line,
                'column': msg.column,
                'message': msg.message
            }
            for msg in messages
        ]
        
        # Convert symbol table
        symbols = semantic.get_symbol_table().get_all_symbols()
        symbol_dict = {
            name: {
                'type': info.var_type.value,
                'line': info.line,
                'used': info.is_used,
                'assigned': info.is_assigned
            }
            for name, info in symbols.items()
        }
        
        # Convert AST to JSON (simplified representation)
        def ast_to_dict(node):
            if hasattr(node, 'children'):
                return {
                    'type': node.type,
                    'value': str(node.value) if hasattr(node, 'value') and node.value else None,
                    'children': [ast_to_dict(child) for child in node.children]
                }
            else:
                return {
                    'type': 'Terminal',
                    'value': str(node)
                }
        
        ast_list = [ast_to_dict(node) for node in ast]
        
        return jsonify({
            'success': success,
            'messages': message_list,
            'tokens': token_list,
            'ast': ast_list,
            'symbolTable': symbol_dict
        })
    
    except SyntaxError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'messages': [{
                'code': 'SYNTAX',
                'severity': 'ERROR',
                'line': 0,
                'column': 0,
                'message': str(e)
            }]
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'messages': [{
                'code': 'INTERNAL',
                'severity': 'ERROR',
                'line': 0,
                'column': 0,
                'message': f'Internal error: {str(e)}'
            }]
        }), 500

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Return available sample programs."""
    samples = {
        'simple_declaration': 'int x;',
        'declaration_and_assignment': 'int x;\nx = 5;',
        'multiple_variables': 'int x;\nint y;\nstring s;\nx = 10;\ny = 20;\ns = "hello";',
        'arithmetic': 'int x;\nint y;\nint sum;\nx = 5;\ny = 10;\nsum = x + y;',
        'string_concat': 'string s1;\nstring s2;\nstring result;\ns1 = "hello";\ns2 = " world";\nresult = s1 + s2;',
        'error_type_mismatch': 'int x;\nx = "hello";',
        'error_undeclared': 'x = 5;',
        'error_incompatible_binop': 'int x;\nstring s;\nint result;\nx = 5;\ns = "text";\nresult = x + s;',
    }
    return jsonify(samples)

@app.route('/api/grammar', methods=['GET'])
def get_grammar():
    """Return the language grammar."""
    grammar = {
        'rules': [
            '<program> ::= <stmt_list>',
            '<stmt_list> ::= <stmt> <stmt_list> | epsilon',
            '<stmt> ::= <declaration> | <assignment>',
            '<declaration> ::= <type> <id> ;',
            '<assignment> ::= <id> = <expr> ;',
            '<expr> ::= <term> <expr_prime>',
            '<expr_prime> ::= + <term> <expr_prime> | epsilon',
            '<term> ::= <id> | <num> | <str>'
        ],
        'tokens': {
            '<type>': 'int | string',
            '<id>': '[A-Za-z_][A-Za-z0-9_]*',
            '<num>': '[0-9]+',
            '<str>': '"[^"]*"',
            '<op>': '+ | = | ;'
        }
    }
    return jsonify(grammar)

@app.route('/api/errors', methods=['GET'])
def get_errors():
    """Return error code reference."""
    errors = {
        'E001': 'Variable already declared',
        'E002': 'Variable used before declaration',
        'E003': 'Type mismatch in assignment',
        'E004': 'Incompatible types in binary operation',
        'W001': 'Variable declared but never used'
    }
    return jsonify(errors)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    setup_grammar()
    app.run(debug=True, port=5000)
