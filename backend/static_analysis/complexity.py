import ast

def estimate_complexity(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Unknown (syntax error)"

    max_depth = 0
    current_depth = 0

    class ComplexityVisitor(ast.NodeVisitor):
        def visit_For(self, node):
            nonlocal max_depth, current_depth
            current_depth += 1
            max_depth = max(max_depth, current_depth)
            self.generic_visit(node)
            current_depth -= 1

        def visit_While(self, node):
            # treat while loops same as for loops
            self.visit_For(node)

        def visit_FunctionDef(self, node):
            # reset depth per function
            nonlocal current_depth
            current_depth = 0
            self.generic_visit(node)

    ComplexityVisitor().visit(tree)

    if max_depth == 0:
        return "O(1)"
    elif max_depth == 1:
        return "O(n)"
    elif max_depth == 2:
        return "O(n^2)"
    elif max_depth == 3:
        return "O(n^3)"
    else:
        return "O(n^k)"  # very deep nesting

