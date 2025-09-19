#!/usr/bin/env python3

import argparse, fnmatch, hashlib, sys, yaml, os
from pathlib import Path
from datetime import datetime

DEFAULT_LIB_SUBMODULE = "libs/EL-KiCad-Library"
IGNORE_FILE = ".kicadprojignore"

def read_ignore_patterns(root: Path):
    p = root / IGNORE_FILE
    if not p.exists(): return []
    return [line.strip() for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]

def is_ignored(path: Path, root: Path, patterns):
    rel = path.relative_to(root).as_posix()
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)

def discover_projects(root: Path, patterns):
    projects = []
    for p in root.rglob("*.kicad_pro"):
        if is_ignored(p, root, patterns): continue
        projects.append(p.parent)
    # Deduplicate and sort
    return sorted(set(projects))

def load_manifest(root: Path, manifest_path: Path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    proj_dirs = [root / Path(p) for p in data.get("projects", [])]
    return [p for p in proj_dirs if p.exists()]

def backup(path: Path):
    if path.exists():
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        b = path.with_suffix(path.suffix + f".bak.{ts}")
        b.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  backup: {b.name}")

def filehash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]

def build_sym_table(lib_root_rel: str, lib_root_abs: Path):
    sym_dir = lib_root_abs / "symbols"
    lines = ["(sym_lib_table\n"]
    if sym_dir.exists():
        for f in sorted(sym_dir.glob("*.kicad_sym")):
            name = f.stem
            uri = f'${{KIPRJMOD}}/{lib_root_rel}/symbols/{f.name}'
            lines.append(f'  (lib (name "{name}") (type "KiCad") (uri "{uri}"))\n')
    lines.append(")\n")
    return "".join(lines)

def build_fp_table(lib_root_rel: str, lib_root_abs: Path):
    fp_dir = lib_root_abs / "footprints"
    lines = ["(footprint_lib_table\n"]
    if fp_dir.exists():
        for d in sorted(fp_dir.iterdir()):
            if d.is_dir() and d.name.endswith(".pretty"):
                name = d.name[:-7] # remove ".pretty"
                uri = f'${{KIPRJMOD}}/{lib_root_rel}/footprints/{d.name}'
                lines.append(f'  (lib (name "{name}") (type "KiCad") (uri "{uri}"))\n')
    lines.append(")\n")
    return "".join(lines)

def write_if_changed(project_dir: Path, fname: str, content: str, dry: bool):
    out = project_dir / fname
    new_hash = filehash(content)
    old_hash = filehash(out.read_text(encoding="utf-8")) if out.exists() else None
    if new_hash == old_hash:
        print(f"  | {fname}: unchanged")
        return
    if dry:
        print(f"  - {fname}: would write")
        return
    backup(out)
    out.write_text(content, encoding="utf-8")
    print(f"{fname}: updated")

def main():
    ap = argparse.ArgumentParser(description="Generate KiCad project tables for all projects in this repo.")
    ap.add_argument("--repo-root", default=".", help="Path to the product repo root (default: current dir)")
    ap.add_argument("--lib-submodule", default=DEFAULT_LIB_SUBMODULE,
                    help="Path (from repo root) to EL-KiCad-Library submodule")
    ap.add_argument("--manifest", help="Optional YAML file listing projects to update")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    lib_root_abs = (repo_root / args.lib_submodule).resolve()

    if not lib_root_abs.exists():
        sys.exit(f"Library submodule not found at: {lib_root_abs}")

    # Determine projects
    if args.manifest:
        projects = load_manifest(repo_root, Path(args.manifest))
    else:
        patterns = read_ignore_patterns(repo_root)
        projects = discover_projects(repo_root, patterns)

    if not projects:
        sys.exit("No KiCad projects found.")

    print(f"Repo root: {repo_root}")
    print(f"Library submodule: {lib_root_abs}")

    for proj in projects:
        rel = os.path.relpath(lib_root_abs, start=proj).replace("\\", "/")
        print(f"\nProject: {proj.relative_to(repo_root)}")
        print(f"  relative lib path: {rel}")

        sym = build_sym_table(rel, lib_root_abs)
        fp  = build_fp_table(rel, lib_root_abs)

        write_if_changed(proj, "sym-lib-table", sym, args.dry_run)
        write_if_changed(proj, "fp-lib-table",  fp,  args.dry_run)

    print("\nDone.")

if __name__ == "__main__":
    try:
        import yaml  # pyyaml
    except Exception:
        sys.exit("Missing the 'pyyaml'. You can simply install it using 'pip install pyyaml'")
    main()
