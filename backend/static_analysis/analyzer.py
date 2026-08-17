import ast


BUILTINS = {
    "print", "len", "range", "int", "float", "str", "list", "dict",
    "set", "tuple", "bool", "sum", "min", "max", "abs", "round",
    "enumerate", "zip", "map", "filter", "sorted", "reversed",
    "isinstance", "type", "super", "object"
}


class StaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.defined_vars = set()
        self.used_vars = set()

        # Stack of scopes. Each function gets its own scope.
        self.scopes = [set()]

        # Track variables used anywhere in the program.
        self.all_defined_vars = set()
        self.all_used_vars = set()

    def current_scope(self):
        return self.scopes[-1]

    def is_defined(self, name):
        # Check current scope first, then outer scopes.
        for scope in reversed(self.scopes):
            if name in scope:
                return True

        return name in BUILTINS

    def visit_FunctionDef(self, node):
        # The function name is defined in the current scope.
        self.current_scope().add(node.name)
        self.all_defined_vars.add(node.name)

        # Create a new local scope.
        local_scope = set()

        # Function parameters are definitions.
        for arg in node.args.args:
            local_scope.add(arg.arg)

        self.scopes.append(local_scope)

        # Analyze the function body separately.
        self._visit_block(node.body)

        self.scopes.pop()

    def visit_Assign(self, node):
        # Analyze the RHS first.
        self.visit(node.value)

        # Then define the assigned variables.
        for target in node.targets:
            self._define_target(target)

    def visit_AnnAssign(self, node):
        if node.value:
            self.visit(node.value)

        self._define_target(node.target)

    def visit_AugAssign(self, node):
        # x += 1 uses x before assigning to it.
        self.visit(node.target)
        self.visit(node.value)

        if isinstance(node.target, ast.Name):
            self._define_target(node.target)

    def _define_target(self, target):
        if isinstance(target, ast.Name):
            self.current_scope().add(target.id)
            self.all_defined_vars.add(target.id)

        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self._define_target(element)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.all_used_vars.add(node.id)

            if not self.is_defined(node.id):
                self.issues.append(
                    f"Variable '{node.id}' may be used before definition "
                    f"(line {node.lineno})"
                )

    def _visit_block(self, statements):
        reachable = True

        for statement in statements:
            if not reachable:
                self.issues.append(
                    f"Unreachable code detected at line {statement.lineno}"
                )

            self.visit(statement)

            # A return makes subsequent statements in this block unreachable.
            if isinstance(statement, ast.Return):
                reachable = False

    def visit_If(self, node):
        self.visit(node.test)

        self._visit_block(node.body)

        if node.orelse:
            self._visit_block(node.orelse)

    def visit_For(self, node):
        self.visit(node.iter)
        self._define_target(node.target)
        self._visit_block(node.body)

        if node.orelse:
            self._visit_block(node.orelse)

    def visit_While(self, node):
        self.visit(node.test)
        self._visit_block(node.body)

        if node.orelse:
            self._visit_block(node.orelse)

    def visit_Return(self, node):
        if node.value:
            self.visit(node.value)


def run_static_analysis(code):
    """Run lightweight AST-based static checks."""

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

    analyzer.defined_vars = analyzer.all_defined_vars
    analyzer.used_vars = analyzer.all_used_vars

    unused = analyzer.defined_vars - analyzer.used_vars

    return {
        "syntax_error": None,
        "issues": analyzer.issues,
        "unused_variables": sorted(unused)
    }