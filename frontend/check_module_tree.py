#!/usr/bin/env python3
import re
from pathlib import Path
import yaml

try:
    from graphviz import Digraph
except Exception:
    Digraph = None

ROUTE_DECORATORS = re.compile(
    r"@(router|app)\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]", re.I
)

FRONTEND_DIRS = ["frontend/src/modules", "frontend/src/features"]
BACKEND_DIRS = ["backend/app", "backend"]

# Aliases: jei repo turi "estimate" arba "progress", laikome, kad įgyvendinta dalis SmartRP punktų
ESTIMATE_ALIASES = {
    "Projekto aprašymo analizė",
    "Medžiagų sąmata",
    "Darbo sąnaudos",
    "Įrankių poreikis",
    "Kainodara (NOK)",
    "Ataskaitų generavimas",
    "API integracija",
}
PROGRESS_ALIASES = {"Progreso sekimas"}


def load_expected(yaml_path: Path):
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("SmartRP", [])
    data.setdefault("CZReco", [])
    return data


def find_frontend_modules(root: Path):
    found = set()
    for d in FRONTEND_DIRS:
        p = root / d
        if p.exists():
            for item in p.rglob("*"):
                if item.is_dir():
                    has_code = any(
                        ch.suffix in {".tsx", ".ts", ".jsx", ".js"}
                        for ch in item.iterdir()
                        if ch.is_file()
                    )
                    if has_code:
                        found.add(item.name.lower())
    return sorted(found)


def find_backend_modules(root: Path):
    found = set()
    for d in BACKEND_DIRS:
        p = root / d
        if p.exists():
            for item in p.rglob("*"):
                if item.is_dir() and any(
                    (item / fn).exists()
                    for fn in ("routes.py", "schemas.py", "services.py", "__init__.py")
                ):
                    found.add(item.name.lower())
    return sorted(found)


def collect_fastapi_routes(root: Path):
    seen = set()
    routes = []
    for d in BACKEND_DIRS:
        p = root / d
        if p.exists():
            for py in p.rglob("*.py"):
                try:
                    text = py.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for m in ROUTE_DECORATORS.finditer(text):
                    who, method, path = m.groups()
                    key = (method.upper(), str(py.relative_to(root)), path)
                    if key not in seen:
                        seen.add(key)
                        routes.append(key)
    routes.sort(key=lambda x: (x[2], x[0]))
    return routes


def is_present(name: str, backend_mods, frontend_mods):
    name_low = name.lower()
    if name_low in backend_mods or name_low in frontend_mods:
        return True
    if (
        "estimate" in backend_mods or "estimate" in frontend_mods
    ) and name in ESTIMATE_ALIASES:
        return True
    if (
        "progress" in backend_mods or "progress" in frontend_mods
    ) and name in PROGRESS_ALIASES:
        return True
    return False


def render_graph(expected, backend_mods, frontend_mods, out_base="module_tree_diagram"):
    if Digraph is None:
        return None
    dot = Digraph(comment="SmartRP + CZReco Module Tree", format="png")
    dot.attr(rankdir="LR", fontsize="12")
    dot.attr(
        "node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="11"
    )

    dot.node("SmartRP", f"SmartRP ({len(expected['SmartRP'])})", color="deepskyblue")
    dot.node("CZReco", f"CZReco ({len(expected['CZReco'])})", color="springgreen")

    for name in expected["SmartRP"]:
        fill = "white" if is_present(name, backend_mods, frontend_mods) else "lightgray"
        dot.node(f"S_{name}", name, color="deepskyblue", fillcolor=fill)
        dot.edge("SmartRP", f"S_{name}")

    for name in expected["CZReco"]:
        fill = "white" if is_present(name, backend_mods, frontend_mods) else "lightgray"
        dot.node(f"C_{name}", name, color="springgreen", fillcolor=fill)
        dot.edge("CZReco", f"C_{name}")

    return dot.render(out_base, format="png", cleanup=True)


def main():
    root = Path(".").resolve()
    expected = load_expected(Path("modules_expected.yaml"))
    backend_mods = find_backend_modules(root)
    frontend_mods = find_frontend_modules(root)
    routes = collect_fastapi_routes(root)

    report = []
    report.append("# SmartRP + CZReco – Module Tree Report\n")
    report.append("## Summary")
    report.append(f"- Expected SmartRP: {len(expected['SmartRP'])}")
    report.append(f"- Expected CZReco: {len(expected['CZReco'])}")
    report.append(f"- Found backend modules: {len(backend_mods)}")
    report.append(f"- Found frontend modules: {len(frontend_mods)}\n")

    report.append("## SmartRP (expected)")
    for n in expected["SmartRP"]:
        mark = "✅" if is_present(n, backend_mods, frontend_mods) else "❌"
        report.append(f"- {mark} {n}")
    report.append("\n## CZReco (expected)")
    for n in expected["CZReco"]:
        mark = "✅" if is_present(n, backend_mods, frontend_mods) else "❌"
        report.append(f"- {mark} {n}")

    report.append("\n## Backend modules (discovered)")
    report += [f"- {m}" for m in backend_mods] or ["- (none)"]

    report.append("\n## Frontend modules (discovered)")
    report += [f"- {m}" for m in frontend_mods] or ["- (none)"]

    report.append("\n## FastAPI routes (discovered)")
    if routes:
        for method, file, path in routes:
            report.append(f"- `{method}` {path}  _(in {file})_")
    else:
        report.append("- (none)")

    Path("module_tree_report.md").write_text("\n".join(report), encoding="utf-8")

    out = render_graph(expected, backend_mods, frontend_mods)
    if out:
        print(f"Diagram: {out}")
    print("Report: module_tree_report.md")


if __name__ == "__main__":
    main()
