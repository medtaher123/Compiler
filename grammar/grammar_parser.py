from collections import defaultdict

# Special constants
EPSILON = 'epsilon'
EOF = '$'


class GrammarAnalyzer:
    def __init__(self):
        self.grammar = defaultdict(list)
        self.non_terminals = set()
        self.terminals = set()
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.start_symbol = None

    def load_from_file(self, filepath):
        """Reads a BNF file and builds the grammar dictionary."""
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or '::=' not in line:
                    continue

                # Split Left Hand Side (LHS) and Right Hand Side (RHS)
                lhs, rhs = line.split('::=')
                lhs = lhs.strip()
                self.non_terminals.add(lhs)

                # Set the first rule as the start symbol
                if self.start_symbol is None:
                    self.start_symbol = lhs

                # Split multiple rules separated by '|'
                for production in rhs.split('|'):
                    symbols = production.strip().split()
                    self.grammar[lhs].append(symbols)

        # Identify Terminals: Any symbol not in non_terminals (and not epsilon)
        for rules in self.grammar.values():
            for production in rules:
                for symbol in production:
                    if symbol not in self.non_terminals and symbol != EPSILON:
                        self.terminals.add(symbol)

    def load_from_string(self, grammar_str):
        """Reads a BNF grammar from a string input."""
        for line in grammar_str.strip().splitlines():
            line = line.strip()
            if not line or '::=' not in line:
                continue

            # Split Left Hand Side (LHS) and Right Hand Side (RHS)
            lhs, rhs = line.split('::=')
            lhs = lhs.strip()
            self.non_terminals.add(lhs)

            # Set the first rule as the start symbol
            if self.start_symbol is None:
                self.start_symbol = lhs

            # Split multiple rules separated by '|'
            for production in rhs.split('|'):
                symbols = production.strip().split()
                self.grammar[lhs].append(symbols)

        # Identify Terminals: Any symbol not in non_terminals (and not epsilon)
        for rules in self.grammar.values():
            for production in rules:
                for symbol in production:
                    if symbol not in self.non_terminals and symbol != EPSILON:
                        self.terminals.add(symbol)

    def compute_first(self):
        """Calculates the FIRST sets for all non-terminals."""
        # Initialize FIRST sets for terminals to themselves
        for terminal in self.terminals:
            self.first[terminal] = {terminal}

        # Initialize FIRST sets for non-terminals to empty
        for nt in self.non_terminals:
            self.first[nt] = set()

        changed = True
        while changed:
            changed = False
            for lhs, productions in self.grammar.items():
                for production in productions:
                    # If the rule is 'epsilon', add it to FIRST(lhs)
                    if production == [EPSILON]:
                        if EPSILON not in self.first[lhs]:
                            self.first[lhs].add(EPSILON)
                            changed = True
                        continue

                    # Otherwise, go through the symbols in the production
                    for symbol in production:
                        symbol_first = self.first[symbol]

                        # Add everything except epsilon
                        for f in symbol_first - {EPSILON}:
                            if f not in self.first[lhs]:
                                self.first[lhs].add(f)
                                changed = True

                        # If this symbol cannot produce epsilon, we stop looking further
                        if EPSILON not in symbol_first:
                            break
                    else:
                        # If the loop finished without breaking, ALL symbols can produce epsilon!
                        if EPSILON not in self.first[lhs]:
                            self.first[lhs].add(EPSILON)
                            changed = True

    def compute_first1(self):
        """Calculates the FIRST sets for all non-terminals."""
        # Initialize FIRST sets for terminals to themselves
        for terminal in self.terminals:
            self.first[terminal] = {terminal}

        # Initialize FIRST sets for non-terminals to empty
        for nt in self.non_terminals:
            self.first[nt] = set()

        changed = True
        while changed:
            changed = False
            for lhs, productions in self.grammar.items():
                if EPSILON in [self.first[symbol] for production in productions for symbol in production]:
                    if EPSILON not in self.first[lhs]:
                        self.first[lhs].add(EPSILON)
                        changed = True
                else:
                    pass


    def compute_follow(self):
        """Calculates the FOLLOW sets for all non-terminals."""
        # Initialize FOLLOW sets to empty, except Start Symbol gets EOF
        for nt in self.non_terminals:
            self.follow[nt] = set()
        self.follow[self.start_symbol].add(EOF)

        changed = True
        while changed:
            changed = False
            for lhs, productions in self.grammar.items():
                for production in productions:
                    # Look at every symbol in the production
                    for i, symbol in enumerate(production):
                        if symbol in self.non_terminals:
                            # What comes AFTER this non-terminal?
                            following_symbols = production[i + 1:]

                            # Calculate FIRST of the sequence following the non-terminal
                            sequence_first = set()
                            epsilon_in_all = True

                            for next_symbol in following_symbols:
                                f_set = self.first[next_symbol]
                                sequence_first.update(f_set - {EPSILON})
                                if EPSILON not in f_set:
                                    epsilon_in_all = False
                                    break

                            # Add the calculated FIRST set to the FOLLOW set
                            for f in sequence_first:
                                if f not in self.follow[symbol]:
                                    self.follow[symbol].add(f)
                                    changed = True

                            # If there's nothing after it, OR everything after it can be epsilon:
                            # FOLLOW(LHS) gets added to FOLLOW(symbol)
                            if len(following_symbols) == 0 or epsilon_in_all:
                                for f in self.follow[lhs]:
                                    if f not in self.follow[symbol]:
                                        self.follow[symbol].add(f)
                                        changed = True

    def display_results(self):
        print("--- FIRST SETS ---")
        for nt in self.non_terminals:
            print(f"FIRST({nt:10}) = {{ {', '.join(self.first[nt])} }}")

        print("\n--- FOLLOW SETS ---")
        for nt in self.non_terminals:
            print(f"FOLLOW({nt:9}) = {{ {', '.join(self.follow[nt])} }}")

    def build_parsing_table(self):
        """Builds the LL(1) parsing table using FIRST and FOLLOW sets."""
        # The table will be a dictionary of dictionaries: table[NonTerminal][Terminal] = Production
        self.parsing_table = {}
        for nt in self.non_terminals:
            self.parsing_table[nt] = {}

        for lhs, productions in self.grammar.items():
            for production in productions:

                # Step 1: Calculate the FIRST set of the specific production rule (the RHS)
                production_first = set()
                epsilon_in_production = True

                if production == [EPSILON]:
                    production_first.add(EPSILON)
                else:
                    for symbol in production:
                        if symbol in self.terminals:
                            production_first.add(symbol)
                            epsilon_in_production = False
                            break
                        elif symbol in self.non_terminals:
                            f_set = self.first[symbol]
                            production_first.update(f_set - {EPSILON})
                            if EPSILON not in f_set:
                                epsilon_in_production = False
                                break

                # Step 2: Apply the FIRST Rule
                for terminal in production_first - {EPSILON}:
                    # Conflict check to ensure the grammar is actually LL(1)
                    if terminal in self.parsing_table[lhs]:
                        print(f"\033[31mLL(1) CONFLICT DETECTED at Table[{lhs}][{terminal}]!\033[0m")
                    self.parsing_table[lhs][terminal] = production

                # Step 3: Apply the FOLLOW Rule
                if epsilon_in_production or EPSILON in production_first:
                    for terminal in self.follow[lhs]:
                        if terminal in self.parsing_table[lhs]:
                            # Only warn if it's a different rule trying to occupy the same cell
                            if self.parsing_table[lhs][terminal] != production:
                                print(f"\033[31mLL(1) CONFLICT DETECTED at Table[{lhs}][{terminal}]!\033[0m")
                        self.parsing_table[lhs][terminal] = production

    def display_table(self):
        print("\n--- LL(1) PARSING TABLE ---")
        for nt in self.non_terminals:
            for terminal, production in self.parsing_table[nt].items():
                prod_str = " ".join(production)
                print(f"Table[{nt:10}][ {terminal:10} ] = {nt} -> {prod_str}")

    def display_table_pretty(self):
        # Gather all terminals for columns (adding $ for EOF)
        all_terminals = sorted(list(self.terminals)) + [EOF]

        # Calculate column width based on the longest production or terminal name
        col_width = 15
        for nt in self.non_terminals:
            for term in all_terminals:
                prod = self.parsing_table[nt].get(term)
                if prod:
                    col_width = max(col_width, len(" ".join(prod)) + len(nt) + 5)

        print("\n" + "=" * 50)
        print("          LL(1) PREDICTIVE PARSING TABLE")
        print("=" * 50 + "\n")

        # Header Row
        header = f"{'NON-TERMINAL':<15} | " + " | ".join(f"{t:<{col_width}}" for t in all_terminals)
        print(header)
        print("-" * len(header))

        # Data Rows
        for nt in sorted(list(self.non_terminals)):
            row = f"{nt:<15} | "
            cells = []
            for terminal in all_terminals:
                production = self.parsing_table[nt].get(terminal)
                if production:
                    prod_str = f"{nt} -> {' '.join(production)}"
                    cells.append(f"{prod_str:<{col_width}}")
                else:
                    cells.append(f"{'-':<{col_width}}")
            print(row + " | ".join(cells))

# --- Run the Script ---
if __name__ == "__main__":
    analyzer = GrammarAnalyzer()
    #analyzer.load_from_file('grammar.txt')
    analyzer.load_from_string("""
    E ::= T E'
    E' ::= + T E' | epsilon
    T ::= F T'
    T' ::= * F T' | epsilon
    F ::= ( E ) | id
    """)
    analyzer.compute_first()
    analyzer.compute_follow()
    analyzer.display_results()
    analyzer.build_parsing_table()
    analyzer.display_table_pretty()