import ast

def loop_depth_hint(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "unknown"

    max_depth = 0

    def visit(node, depth=0):
        nonlocal max_depth
        if isinstance(node, (ast.For, ast.While)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree)

    if max_depth == 0:
        return "O(1)"
    if max_depth == 1:
        return "O(n)"
    return f"O(n^{max_depth})"
