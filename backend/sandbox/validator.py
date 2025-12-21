import ast

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.With,
    ast.Global,
    ast.Nonlocal,
    ast.Lambda,
)

FORBIDDEN_CALLS = {
    "open",
    "exec",
    "eval",
    "__import__",
    "compile",
    "input",
}

def validate_code(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

    for node in ast.walk(tree):

        if isinstance(node, FORBIDDEN_NODES):
            return False, f"Forbidden syntax: {type(node).__name__}"

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_CALLS:
                    return False, f"Forbidden function call: {node.func.id}"

            if isinstance(node.func, ast.Attribute):
                return False, "Calling object attributes is not allowed"

        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                return False, f"Forbidden dunder attribute: {node.attr}"

        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value in (True, 1):
                return False, "Potential infinite loop detected"

    return True, None
