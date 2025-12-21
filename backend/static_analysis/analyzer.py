import ast

class StaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.defined_vars = set()
        self.used_vars = set()
        self.reachable = True  # for unreachable code detection

    def visit_Assign(self, node):
        # Track defined variables
        if isinstance(node.targets[0], ast.Name):
            self.defined_vars.add(node.targets[0].id)

        # If code is not reachable, warn
        if not self.reachable:
            self.issues.append(f"Unreachable code detected at line {node.lineno}")

        self.generic_visit(node)

    def visit_Name(self, node):
        # Using a variable
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)

            # Undefined use
            if node.id not in self.defined_vars:
                self.issues.append(
                    f"Variable '{node.id}' may be used before definition (line {node.lineno})"
                )

        # If unreachable
        if not self.reachable:
            self.issues.append(f"Unreachable code detected at line {node.lineno}")

        self.generic_visit(node)

    def visit_Return(self, node):
        # After return, everything is unreachable
        self.reachable = False
        self.generic_visit(node)

def run_static_analysis(code):
    """Runs static checks and returns results as a dict."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "syntax_error": str(e),
            "issues": [],
            "unused_variables": []
        }

    analyzer = StaticAnalyzer()
    analyzer.visit(tree)

    # Detect unused variables
    unused = analyzer.defined_vars - analyzer.used_vars

    return {
        "syntax_error": None,
        "issues": analyzer.issues,
        "unused_variables": list(unused)
    }
