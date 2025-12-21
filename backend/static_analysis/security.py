import ast

def security_checks(code):
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["Syntax error — security checks skipped."]

    for node in ast.walk(tree):

        # Dangerous functions
        if isinstance(node, ast.Call):
            func = getattr(node.func, "id", None)

            if func == "eval":
                issues.append("Use of eval() is insecure (line {})".format(node.lineno))

            if func == "exec":
                issues.append("Use of exec() is unsafe (line {})".format(node.lineno))

        # Hardcoded passwords / secrets
        if isinstance(node, ast.Assign):

            # Only check simple assignments like: password = "123"
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):

                target = node.targets[0]
                if isinstance(target, ast.Name):

                    name = target.id.lower()
                    if "password" in name or "secret" in name or "token" in name:
                        issues.append(
                            f"Hardcoded secret detected in variable '{target.id}' (line {node.lineno})"
                        )

    return issues
