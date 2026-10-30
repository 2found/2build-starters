#!/usr/bin/env python3
"""Static harness checks mirroring 2build's harness-audit contract.

`python3 tests/harness.py` composes common/ + each template (the overlay only;
scaffold output is not available) and checks it. verify.py calls check_project()
on every really generated project, where package.json scripts are also checked.
"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"```bash\n(.*?)```", re.S)
SCRIPT = re.compile(r"^(?:bun run|pnpm run|pnpm) ([a-z][\w:-]*)")
PNPM_BUILTINS = {"install", "add", "dlx", "exec", "pkg", "start"}
REQUIRED_2BUILD = ["- Git:", "- QA harness: `.babysit/qa.yaml`", "- Default run:", "- Search: use `rg`"]
BROWSER_2BUILD = ["- Browser:", "- Browser hygiene:"]
QA_LINE = "QA must prove the local target or name the blocker, and must include at least one non-happy-path case before PASS."
NON_HAPPY = re.compile(r"\b(400|404|invalid|reject|error|not[- ]found|empty|missing)\b", re.I)


def anchors(markdown):
    slugs = set()
    for heading in re.findall(r"^#{1,6} (.+)$", markdown, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.strip().lower().replace("`", "")).replace(" ", "-")
        slugs.add(slug)
    return slugs


def section(markdown, title):
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", markdown, re.M | re.S)
    return match.group(1) if match else None


def parse_yaml(path):
    # Bun is already a starter prerequisite; it ships a YAML parser, Python does not.
    out = subprocess.run(["bun", "-e", "console.log(JSON.stringify(Bun.YAML.parse(await Bun.file(process.argv[1]).text())))", str(path)],
                         check=True, text=True, capture_output=True).stdout
    return json.loads(out)


def check_links(project, errors):
    for doc in [project / "AGENTS.md", project / "CLAUDE.md", project / "README.md", project / "DESIGN.md", *sorted((project / "docs").glob("*.md"))]:
        if not doc.exists():
            continue
        for target in LINK.findall(doc.read_text()):
            if re.match(r"^[a-z]+:", target):
                continue
            path, _, anchor = target.partition("#")
            resolved = (doc.parent / path).resolve() if path else doc
            if not resolved.exists():
                errors.append(f"{doc.relative_to(project)}: broken link {target}")
            elif anchor and resolved.suffix == ".md" and anchor not in anchors(resolved.read_text()):
                errors.append(f"{doc.relative_to(project)}: missing anchor {target}")


def check_project(project, template, static=False):
    """Return harness-audit findings for a composed or generated project."""
    project, errors = Path(project), []
    agents_path = project / "AGENTS.md"
    if not agents_path.exists():
        return ["AGENTS.md missing"]
    agents = agents_path.read_text()
    if "AGENTS.md" not in (project / "CLAUDE.md").read_text():
        errors.append("CLAUDE.md does not point at AGENTS.md")
    check_links(project, errors)

    # Project context links: architecture required, design when there is a UI.
    architecture = [t for t in LINK.findall(agents) if re.search(r"docs/ARCHITECT(URE)?[\w-]*\.md$", t)]
    if not architecture:
        errors.append("AGENTS.md links no docs/ARCHITECT*.md")
    if "docs/VERIFY.md" not in agents:
        errors.append("AGENTS.md does not link docs/VERIFY.md")
    ui = (project / "app").is_dir()
    if ui and "(DESIGN.md)" not in agents:
        errors.append("UI project does not link DESIGN.md from AGENTS.md")
    if not ui and not re.search(r"Design\*\* — N/A", agents):
        errors.append("API-only AGENTS.md must state Design N/A")
    deploy = section(agents, "Deploy and release")
    if deploy is None or not ("N/A" in deploy or "RELEASE.md" in deploy):
        errors.append("AGENTS.md needs a Deploy and release section (owner link or explicit N/A)")

    # Run/verify commands must exist and match CI and the catalog.
    for title in ("Run", "Verify"):
        if section(agents, title) is None:
            errors.append(f"AGENTS.md has no ## {title} section")
    verify_block = FENCE.findall(section(agents, "Verify") or "")
    verify_cmds = [line.split("#")[0].strip() for line in (verify_block[0] if verify_block else "").splitlines() if line.strip()]
    catalog_cmds = [" ".join(argv) for argv in template["verify"] if "install" not in argv]
    if verify_cmds != catalog_cmds:
        errors.append(f"AGENTS.md Verify {verify_cmds} != catalog verify {catalog_cmds}")
    workflow = project / ".github/workflows/check.yml"
    ci = workflow.read_text() if workflow.exists() else ""
    for command in catalog_cmds:
        if f"- run: {command}" not in ci:
            errors.append(f"CI does not run `{command}`")
    package = project / "package.json"
    if package.exists() and not static:
        scripts = json.loads(package.read_text()).get("scripts", {})
        commands = [l.split("#")[0].strip() for block in FENCE.findall(agents) for l in block.splitlines()]
        for command in commands + [template["dev"] and " ".join(template["dev"])]:
            match = SCRIPT.match(command or "")
            if match and match.group(1) not in PNPM_BUILTINS | {"test"} and match.group(1) not in scripts:
                errors.append(f"`{command}` names a missing package script")
        for name in ("dev", "test", "typecheck", "build"):
            if name not in scripts:
                errors.append(f"package.json has no {name} script")

    # .babysit/qa.yaml: local target, checks, a non-happy-path flow.
    qa = parse_yaml(project / ".babysit/qa.yaml")
    if not str(qa.get("url", "")).startswith("http://localhost:"):
        errors.append("qa.yaml url is not a local target")
    if qa.get("check") != " && ".join(catalog_cmds):
        errors.append("qa.yaml check differs from the catalog verify list")
    if not NON_HAPPY.search(qa.get("flows", "")):
        errors.append("qa.yaml flows have no non-happy-path case")

    # 2build pointers.
    pointers = section(agents, "2build") or ""
    for bullet in REQUIRED_2BUILD + (BROWSER_2BUILD if ui else []):
        if bullet not in pointers:
            errors.append(f"## 2build lacks `{bullet}`")
    if QA_LINE not in pointers:
        errors.append("## 2build lacks the QA closing sentence")
    if re.search(r"\b(pkill|close --all)\b", pointers.replace("never `kill`/`pkill`/`close --all`", "")):
        errors.append("browser cleanup instruction is unsafe")

    # Secrets: example only, real env files ignored.
    ignore = (project / ".gitignore").read_text().splitlines()
    for rule in (".env", ".env.*", "!.env.example", ".babysit/.env"):
        if rule not in ignore:
            errors.append(f".gitignore lacks {rule}")
    if not (project / ".env.example").exists():
        errors.append(".env.example missing")
    return errors


def compose(template_path, destination):
    for folder in (ROOT / "common", ROOT / template_path):
        shutil.copytree(folder, destination, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("node_modules", "dist", ".next"))


def main():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    failed = False
    for template_id, template in catalog["templates"].items():
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / template_id
            compose(template["path"], project)
            errors = check_project(project, template, static=True)
        for error in errors:
            print(f"FAIL {template_id}: {error}")
        failed |= bool(errors)
        if not errors:
            print(f"PASS {template_id}: harness-audit contract (static overlay)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
