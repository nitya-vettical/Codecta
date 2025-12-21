import ast

def style_checks(code):
    issues = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["Syntax error — style checks skipped"]

    # ---- 1. Check for unused imports ----
    imported = set()
    used = set()

    for node in ast.walk(tree):

        # Collect imported names
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split('.')[0])

        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.name)

        # Track usage
        if isinstance(node, ast.Name):
            used.add(node.id)

        # ---- 2. Check line length ----
        for i, line in enumerate(code.split("\n"), start=1):
            if len(line) > 100:
                issues.append(f"Line {i} exceeds 100 characters (too long).")

        # ---- 3. Bad variable naming (optional basic rule) ----
        if isinstance(node, ast.Name):
            if len(node.id) == 1:
                issues.append(f"Variable '{node.id}' has a non-descriptive name (line {node.lineno}).")

    # Detect unused imports
    unused_imports = imported - used
    for imp in unused_imports:
        issues.append(f"Unused import detected: '{imp}'")

    return issues
