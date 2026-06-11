import os
import re
import json
import ast
from pathlib import Path

ROOT = Path(r"c:\Users\ASUS\Desktop\divyangbot")
EXCLUDE = {"venv", "node_modules", ".git", ".next", "__pycache__"}
FRONTEND_ROOT = ROOT / "frontend"
BACKEND_ROOT = ROOT / "backend"

PY_EXT = {".py"}
TS_EXT = {".ts", ".tsx", ".js", ".jsx"}


def iter_project_files():
    for p in ROOT.rglob("*"):
        if p.is_file():
            if any(part in EXCLUDE for part in p.parts):
                continue
            yield p


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="latin-1")


def parse_py_imports(path):
    text = read_text(path)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                imports.append("." * node.level + module)
            else:
                imports.append(module)
    return imports


def parse_ts_imports(path):
    text = read_text(path)
    regex = re.compile(r"import\s+(?:[\s\S]+?)\s+from\s+['\"]([^'\"]+)['\"]|require\(['\"]([^'\"]+)['\"]\)")
    matches = regex.findall(text)
    imports = []
    for m in matches:
        imp = m[0] or m[1]
        if imp:
            imports.append(imp)
    return imports


def list_pages_components_services():
    pages = []
    components = []
    services = []
    hooks = []
    for p in FRONTEND_ROOT.rglob("*.tsx"):
        rel = p.relative_to(FRONTEND_ROOT).as_posix()
        if "/page.tsx" in rel or rel == "app/page.tsx":
            pages.append(rel)
        else:
            components.append(rel)
    for p in FRONTEND_ROOT.rglob("*.ts"):
        rel = p.relative_to(FRONTEND_ROOT).as_posix()
        if rel.startswith("services/"):
            services.append(rel)
        if rel.startswith("utils/"):
            hooks.append(rel)
    return pages, components, services, hooks


def find_api_calls():
    calls = {}
    api_files = list(FRONTEND_ROOT.rglob("*.ts")) + list(FRONTEND_ROOT.rglob("*.tsx"))
    pattern = re.compile(r"fetch\(['\"](.*?)['\"]|axios\.(?:get|post|put|delete)\(['\"](.*?)['\"]")
    for p in api_files:
        text = read_text(p)
        matches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]|axios\.(?:get|post|put|delete)\(['\"]([^'\"]+)['\"]", text)
        if matches:
            for m in matches:
                endpoint = m[0] or m[1]
                calls.setdefault(p.relative_to(FRONTEND_ROOT).as_posix(), []).append(endpoint)
    return calls


def scan_backend_endpoints():
    endpoints = {}
    for p in BACKEND_ROOT.rglob("*.py"):
        if p.name.startswith("test_"):
            continue
        text = read_text(p)
        for m in re.finditer(r"@app\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]", text):
            method = m.group(1).upper()
            path = m.group(2)
            endpoints.setdefault(p.relative_to(ROOT).as_posix(), []).append((method, path))
        # perhaps app.include_router
        if "include_router" in text:
            endpoints.setdefault(p.relative_to(ROOT).as_posix(), []).append(("INCLUDE_ROUTER", ""))
    return endpoints


def find_env_vars():
    uses = {}
    for p in iter_project_files():
        if p.suffix in PY_EXT | TS_EXT:
            txt = read_text(p)
            envs = set(re.findall(r"os\.getenv\(['\"]([A-Z0-9_]+)['\"]|process\.env\.([A-Z0-9_]+)", txt))
            if envs:
                uses[p.relative_to(ROOT).as_posix()] = sorted({g[0] or g[1] for g in envs})
    return uses


def main():
    all_files = [p.relative_to(ROOT).as_posix() for p in iter_project_files()]
    pages, components, services, hooks = list_pages_components_services()
    api_calls = find_api_calls()
    backend_endpoints = scan_backend_endpoints()
    env_vars = find_env_vars()
    imports = {}
    deps = {}
    for p in iter_project_files():
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix in PY_EXT:
            imports[rel] = parse_py_imports(p)
        elif p.suffix in TS_EXT:
            imports[rel] = parse_ts_imports(p)
        else:
            imports[rel] = []
    # build reverse deps by string contains simple matching from import names
    for src, imps in imports.items():
        for imp in imps:
            deps.setdefault(imp, set()).add(src)
    out = {
        "all_files": all_files,
        "pages": pages,
        "components": components,
        "services": services,
        "hooks": hooks,
        "api_calls": api_calls,
        "backend_endpoints": backend_endpoints,
        "env_vars": env_vars,
        "imports": imports,
        "reverse_deps": {k: sorted(v) for k,v in deps.items()},
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
