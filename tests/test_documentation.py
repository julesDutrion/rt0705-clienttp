import ast
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1] / "client"


def has_direct_return(node):
    pending = list(node.body)
    while pending:
        child = pending.pop()
        if isinstance(child, ast.Return):
            return child.value is not None
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        pending.extend(ast.iter_child_nodes(child))
    return False


def test_public_classes_and_functions_follow_docstring_conventions():
    issues = []
    for path in SOURCE_ROOT.rglob("*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node) or ""
                if not docstring.startswith("Classe qui représente"):
                    issues.append(f"{path}:{node.lineno} {node.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                docstring = ast.get_docstring(node) or ""
                if not docstring.startswith("Méthode qui"):
                    issues.append(f"{path}:{node.lineno} {node.name}")
                    continue
                parameters = [
                    argument.arg
                    for argument in (
                        node.args.posonlyargs
                        + node.args.args
                        + node.args.kwonlyargs
                    )
                    if argument.arg not in {"self", "cls"}
                ]
                for parameter in parameters:
                    if f":param {parameter}:" not in docstring:
                        issues.append(
                            f"{path}:{node.lineno} {node.name}: {parameter}"
                        )
                if has_direct_return(node) and ":return:" not in docstring:
                    issues.append(f"{path}:{node.lineno} {node.name}: return")

    assert issues == []
