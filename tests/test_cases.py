"""
Comprehensive test cases for the compiler.
Tests are organized in categories:
1. VALID: Code that should compile successfully
2. INVALID: Code with semantic errors
3. EDGE_CASES: Boundary and special scenarios
"""

VALID_TESTS = {
    "simple_declaration": """
    int x;
    """,
    
    "declaration_and_assignment": """
    int x;
    x = 5;
    """,
    
    "multiple_declarations": """
    int x;
    int y;
    string s;
    """,
    
    "multiple_assignments": """
    int x;
    int y;
    x = 10;
    y = 20;
    """,
    
    "string_assignment": """
    string greeting;
    greeting = "hello";
    """,
    
    "arithmetic_expression": """
    int x;
    int y;
    x = 5;
    y = 10;
    x = x + y;
    """,
    
    "string_concatenation": """
    string s1;
    string s2;
    string result;
    s1 = "hello";
    s2 = "world";
    result = s1 + s2;
    """,
    
    "complex_arithmetic": """
    int a;
    int b;
    int c;
    a = 5;
    b = 10;
    c = a + b + 15;
    """,
    
    "used_variable": """
    int x;
    x = 42;
    int y;
    y = x + 5;
    """,
}


INVALID_TESTS = {
    "undeclared_variable": """
    x = 5;
    """,
    
    "undeclared_in_expression": """
    int x;
    x = y + 5;
    """,
    
    "type_mismatch_int_to_string": """
    string s;
    s = 42;
    """,
    
    "type_mismatch_string_to_int": """
    int x;
    x = "hello";
    """,
    
    "double_declaration": """
    int x;
    int x;
    """,
    
    "incompatible_binary_operation": """
    int x;
    string s;
    int result;
    x = 5;
    s = "text";
    result = x + s;
    """,
    
    "string_add_int": """
    string s;
    int x;
    s = "hello" + 5;
    """,
    
    "used_before_declared": """
    x = 10;
    int x;
    """,
}


EDGE_CASES = {
    "unused_variable": """
    int x;
    int y;
    y = 10;
    """,
    
    "multiple_unused_variables": """
    int a;
    int b;
    int c;
    int d;
    d = 100;
    """,
    
    "declaration_without_assignment": """
    int x;
    int y;
    y = 5;
    """,
    
    "chain_additions": """
    int a;
    int b;
    int c;
    int result;
    a = 1;
    b = 2;
    c = 3;
    result = a + b + c;
    """,
    
    "reuse_variable": """
    int counter;
    counter = 0;
    counter = counter + 1;
    counter = counter + 1;
    """,
    
    "string_reuse": """
    string msg;
    msg = "first";
    msg = "second";
    """,
    
    "numeric_literal_addition": """
    int x;
    x = 5 + 10;
    """,
    
    "zero_assignment": """
    int x;
    x = 0;
    """,
    
    "empty_string": """
    string s;
    s = "";
    """,
}


if __name__ == "__main__":
    print("=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"\nValid Tests:       {len(VALID_TESTS)}")
    print(f"Invalid Tests:     {len(INVALID_TESTS)}")
    print(f"Edge Cases:        {len(EDGE_CASES)}")
    print(f"Total Test Cases:  {len(VALID_TESTS) + len(INVALID_TESTS) + len(EDGE_CASES)}")
    print("\n" + "=" * 60)