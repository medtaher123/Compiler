# Compiler Project Documentation
 
## Executive Summary
 
This document describes the implementation of a **custom programming language compiler** built in Python. The compiler supports variable declarations, arithmetic operations, and string manipulation with comprehensive semantic analysis and professional error reporting.
 
**Project Scope:** Milestones 1-3 (Lexical Analysis, Syntax Analysis, Semantic Analysis)

## 1. How to Run the App

The project has two parts:
- a Flask backend API in `compiler_api.py`
- a browser UI in `compiler_dashboard.html`

### 1.1 Install dependencies

From the project root:

```bash
python -m pip install -r requirements.txt
```

### 1.2 Start the backend API

Run the Flask server on port `5000`:

```bash
python compiler_api.py
```

You can verify that it is running with:

```bash
curl http://localhost:5000/health
```

### 1.3 Open the UI

The dashboard talks to `http://localhost:5000/api`, so keep the backend running while using the UI.

You can open the dashboard directly in your browser:

```bash
xdg-open index.html
```

If opening the file directly does not work in your browser, serve the folder locally instead:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```
 
---
 
## 2. Project Overview
 
### 1.1 Language Features
 
The compiler supports a simple but functional programming language with:
 
- **Variable Declarations:** `int x;` and `string name;`
- **Variable Assignments:** `x = 5;`, `s = "hello";`
- **Arithmetic Expressions:** `x = 5 + 10;` with automatic type checking
- **String Concatenation:** `s = "hello" + " world";`
- **Expression Chaining:** `result = a + b + c;`
### 1.2 Supported Data Types
 
- **int:** Integer numbers (e.g., `5`, `42`, `1000`)
- **string:** Text values (e.g., `"hello"`)
### 1.3 Operators
 
- **Assignment:** `=`
- **Addition:** `+` (polymorphic: works for both int and string)
- **Punctuation:** `;`, `{`, `}`
---
 
## 2. Compiler Architecture
 
### 2.1 The Three Phases
 
```
Source Code
    ↓
[Phase 1: Lexer] → Tokenization
    ↓
[Phase 2: Parser] → Syntax Analysis (AST Generation)
    ↓
[Phase 3: Semantic Analyzer] → Type Checking & Scope Resolution
    ↓
Success/Error Report
```
 
### 2.2 Key Components
 
#### Lexer (Milestone 1)
**File:** `lexer.py`
 
Converts raw source code into a stream of tokens. Handles:
- Identifier recognition (`[A-Za-z_][A-Za-z0-9_]*`)
- Number literals (`\d+`)
- String literals with escape sequences (`"..."`)
- Keywords (`int`, `string`)
- Operators and punctuation
- Line number tracking for error reporting
**Output:** List of Token objects with metadata (value, line number, type)
 
#### Parser (Milestone 2)
**File:** `RecursiveDescentParser.py`
 
Implements table-driven LL(1) parsing using FIRST/FOLLOW sets.
 
**Grammar (BNF):**
```
<program>      ::= <stmt_list>
<stmt_list>    ::= <stmt> <stmt_list> | epsilon
<stmt>         ::= <declaration> | <assignment>
<declaration>  ::= <type> <id> ;
<assignment>   ::= <id> = <expr> ;
<expr>         ::= <term> <expr_prime>
<expr_prime>   ::= + <term> <expr_prime> | epsilon
<term>         ::= <id> | <num> | <str>
```
 
**Key Features:**
- LL(1) parsing table automatically generated
- Semantic actions embedded during parsing
- AST construction on-the-fly
- Detailed step-by-step parsing trace
**Output:** Abstract Syntax Tree (AST) with semantic nodes
 
#### Semantic Analyzer (Milestone 3)
**File:** `semantic_analyzer.py`
 
Performs type checking, scope resolution, and usage analysis.
 
**Checks:**
1. **Variable Declaration:** Detect duplicate declarations
2. **Scope Checking:** Variables used before declaration
3. **Type Checking:** Assignment types must match declaration types
4. **Expression Type Inference:** Automatic type calculation
5. **Usage Warnings:** Variables declared but never used
**Output:** Compilation messages (errors and warnings) with line/column info
 
---
 
## 3. Milestone 1: Lexical Analysis
 
### 3.1 Implementation (`lexer.py`)
 
The Lexer class reads source code character-by-character and produces tokens.
 
**Token Classes:**
- `IdentifierToken`: Variable names
- `NumberToken`: Integer literals
- `StringToken`: String literals with quotes
- `TypeToken`: Keywords `int`, `string`
- `KeywordToken`: Keywords `if`, `then`, `else`
- `OperatorToken`: `+`, `-`, `*`, `/`, `=`, `>`
- `PunctuationToken`: `;`, `{`, `}`, `(`, `)`
- `EOFToken`: End-of-file marker
**Key Algorithm:**
```python
for each character in source:
    try to match against each TokenClass pattern (in order)
    if match found:
        create token and advance position
        handle whitespace (skip it)
        track line numbers for error reporting
    else:
        raise SyntaxError for illegal character
```
 
**Order Matters:** Keywords must be checked before identifiers, otherwise "int" would become an identifier.
 
### 3.2 Example: Tokenization
 
**Input:**
```
int x;
x = 5 + 2;
```
 
**Output:**
```
TYPE(int), ID(x), ;, ID(x), =, NUM(5), +, NUM(2), ;, $
```
 
### 3.3 Testing
 
```python
from lexer import Lexer
 
code = "int x; x = 5 + 2;"
lexer = Lexer(code)
tokens = lexer.tokenize()
# Returns: [TypeToken('int', 1), IdentifierToken('x', 1), ...]
```
 
---
 
## 4. Milestone 2: Syntax Analysis
 
### 4.1 Grammar Design
 
The grammar is designed to:
- Avoid left recursion (use right recursion with prime rules)
- Support operator precedence (currently only addition at same level)
- Be LL(1) parsable (no conflicts in parsing table)
**Key Rule Transformations:**
 
**Original (left-recursive):**
```
<expr> ::= <expr> + <term> | <term>
```
 
**Transformed (right-recursive):**
```
<expr>       ::= <term> <expr_prime>
<expr_prime> ::= + <term> <expr_prime> | epsilon
```
 
### 4.2 FIRST and FOLLOW Sets
 
**Example FIRST Sets:**
```
FIRST(<term>) = {<id>, <num>, <str>}
FIRST(<expr_prime>) = {+, epsilon}
```
 
**Example FOLLOW Sets:**
```
FOLLOW(<assignment>) = {$}
FOLLOW(<expr>) = {;, +}
```
 
### 4.3 LL(1) Parsing Table
 
The parsing table (9 rows × 5 columns) maps:
```
Table[Non-Terminal][Terminal] → Production Rule
```
 
**Example Entry:**
```
Table[<expr>][<id>] → <term> <expr_prime>
```
 
### 4.4 Table-Driven Parser
 
**Algorithm:**
```
stack = [EOF, <start_symbol>]
while stack not empty:
    top = stack.pop()
    
    if top == lookahead:
        shift (consume token)
    elif top is a production:
        push rule RHS onto stack (reversed)
        execute semantic action
    else:
        error
```
 
### 4.5 Semantic Actions
 
Semantic actions build the AST while parsing:
 
- `BuildDecl`: Pops type, id, and semicolon → creates DeclarationNode
- `BuildAssign`: Pops id, expr, semicolon → creates AssignNode
- `BuildBinOp`: Pops left, op, right → creates BinaryOpNode
### 4.6 Example: Parsing `x = 5 + 2;`
 
```
Stack: [EOF, <program>]
1. Apply <program> → <stmt_list>
2. Apply <stmt_list> → <stmt> <stmt_list>
3. Apply <stmt> → <assignment>
4. Apply <assignment> → <id> = <expr> ;
5. Match x, =
6. Apply <expr> → <term> <expr_prime>
7. Apply <term> → <num>, match 5
8. BuildBinOp action
9. Apply <expr_prime> → + <term> <expr_prime>
10. Match +, <term> → <num>, match 2
11. Apply <expr_prime> → epsilon (end of rule)
12. BuildAssign action, match ;
13. Complete
```
 
**Generated AST:**
```
AssignNode(
  variable: IdentifierNode('x'),
  value: BinaryOpNode(
    operator: '+',
    left: NumberNode(5),
    right: NumberNode(2)
  )
)
```
 
---
 
## 5. Milestone 3: Semantic Analysis
 
### 5.1 Symbol Table
 
**File:** `symbol_table.py`
 
The symbol table maintains:
```python
SymbolInfo(
    name: str,           # Variable name
    var_type: int|string, # Declared type
    line: int,           # Declaration line (for errors)
    column: int,         # Declaration column
    is_used: bool,       # Was the variable referenced?
    is_assigned: bool    # Was a value assigned?
)
```
 
**Operations:**
- `declare(name, type, line)`: Add new variable
- `lookup(name)`: Find variable by name
- `mark_as_used(name)`: Track when variable is read
- `mark_as_assigned(name)`: Track when variable is written
### 5.2 Type Checking
 
**Three Passes:**
 
**Pass 1: Collect Declarations**
- Scan AST for all `DeclarationNode` objects
- Add to symbol table
- Check for duplicate declarations (error E001)
**Pass 2: Check Assignments**
- For each `AssignNode`:
  - Verify variable exists (error E002)
  - Infer type of RHS expression
  - Verify type compatibility (error E003)
**Pass 3: Generate Warnings**
- Find unused variables (warning W001)
- Find unassigned variables (warning W002)
### 5.3 Type Inference
 
Automatically determines expression types:
 
```python
def infer_type(expr_node):
    if expr_node is TerminalNode:
        if token_type == '<num>':
            return INT
        elif token_type == '<str>':
            return STRING
        elif token_type == '<id>':
            return lookup_variable_type()
    
    elif expr_node is BinaryOpNode:
        left_type = infer_type(left_child)
        right_type = infer_type(right_child)
        
        if operator == '+':
            if left_type == right_type:
                return left_type
            else:
                error: incompatible types
```
 
### 5.4 Error Codes
 
| Code | Severity | Description |
|------|----------|-------------|
| E001 | Error | Variable already declared |
| E002 | Error | Variable used before declaration |
| E003 | Error | Type mismatch in assignment |
| E004 | Error | Incompatible types in binary operation |
| W001 | Warning | Variable declared but never used |
| W002 | Warning | Variable declared but never assigned |
 
### 5.5 Example: Semantic Analysis
 
**Input:**
```python
int x;
x = "hello";  # Type mismatch!
```
 
**Analysis:**
1. Process declaration: x is int
2. Process assignment: x = "hello"
   - Lookup x: found, type int
   - Infer "hello" type: string
   - Compare: int ≠ string
   - **Error E003: Type mismatch**
**Output:**
```
✗ [E003] ERROR: Type mismatch: 'x' is int but assigned string (Line 2, Col 0)
```
 
---
 
## 6. Error Reporting
 
### 6.1 Professional Error Messages
 
**File:** `error_reporter.py`
 
Features:
- Color-coded output (red for errors, yellow for warnings)
- Line/column information
- Source code display
- Caret (^) pointer to error location
### 6.2 Example Output
 
```
✗ [E002] ERROR: Variable 'y' used before declaration
  Line 2: x = y + 5;
          ^^
 
Compilation failed: 1 error
```
 
### 6.3 Symbol Table Display
 
```
Symbol Table:
──────────────────────────────────────────────────
Variable        Type       Line   Used   Assigned
──────────────────────────────────────────────────
x               int        1      ✓      ✓
y               int        2      ✗      ✗
──────────────────────────────────────────────────
```
 
---
 
## 7. Testing Strategy
 
### 7.1 Test Categories
 
**File:** `test_cases.py` and `test_runner.py`
 
- **Valid Tests (9 cases):** Code that should compile successfully
- **Invalid Tests (8 cases):** Code with semantic errors
- **Edge Cases (9 cases):** Boundary conditions and special scenarios
### 7.2 Running Tests
 
```bash
# Run basic test suite (valid + edge cases)
python test_runner.py
 
# Run all tests including error detection
python test_runner.py all
 
# Show detailed error detection examples
python test_runner.py invalid
 
# Interactive mode
python test_runner.py interactive
```
 
### 7.3 Example Test Case
 
```python
VALID_TESTS = {
    "arithmetic_expression": """
    int x;
    int y;
    x = 5;
    y = 10;
    x = x + y;
    """
}
```
 
---
