from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_pillow(repo: Path) -> None:
    tools_dir = repo / ".tools" / "pillow"
    if tools_dir.exists():
        sys.path.insert(0, str(tools_dir))
        return

    if shutil.which("python3") is None:
        raise RuntimeError("python3 not found")

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--target",
        str(tools_dir),
        "pillow==10.4.0",
    ]
    subprocess.check_call(cmd, cwd=str(repo))
    sys.path.insert(0, str(tools_dir))


def _run_likec4(repo: Path, use_dot: bool = False) -> None:
    if shutil.which("likec4") is None:
        raise RuntimeError("likec4 not found in PATH")

    c4_dir = repo / "src" / "c4"
    subprocess.check_call(["likec4", "validate", str(c4_dir)], cwd=str(repo))
    cmd = [
        "likec4",
        "export",
        "png",
        "--theme",
        "light",
        "-o",
        "./png",
        str(c4_dir),
    ]
    if use_dot and shutil.which("dot"):
        cmd.insert(cmd.index("export") + 2, "--use-dot")
    subprocess.check_call(cmd, cwd=str(repo))


def _get_export_version(repo: Path) -> str:
    spec = repo / "src" / "c4" / "__spec.c4"
    if not spec.exists():
        return "1.0"
    raw = spec.read_text(encoding="utf-8")
    m = re.search(r"//\s*version\s*:\s*(\S+)", raw, re.IGNORECASE)
    return m.group(1).strip() if m else "1.0"


def _flatten_pngs(repo: Path) -> int:
    _ensure_pillow(repo)
    from PIL import Image  # type: ignore

    Image.MAX_IMAGE_PIXELS = None

    png_dir = repo / "png"
    files = sorted(str(p) for p in png_dir.rglob("*.png") if p.is_file())
    version = _get_export_version(repo)
    exported = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    png_info = {"version": version, "Software": "LikeC4 export", "exported": exported}
    for p in files:
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        out = Image.alpha_composite(bg, im).convert("RGB")
        out.save(p, format="PNG", optimize=True, info=png_info)
    return len(files)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Export LikeC4 to PNG with white background")
    parser.add_argument(
        "--flatten-only",
        action="store_true",
        help="Only apply white background to existing PNG in png/, skip likec4 export",
    )
    parser.add_argument(
        "--use-dot",
        action="store_true",
        help="Use graphviz (dot) for export; avoids preview server if it fails",
    )
    args = parser.parse_args()

    repo = _repo_root()
    os.makedirs(repo / "png", exist_ok=True)

    if not args.flatten_only:
        _run_likec4(repo, use_dot=args.use_dot)
    count = _flatten_pngs(repo)

    index_png = repo / "png" / "index.png"
    if index_png.exists():
        index_png.unlink()

    sys.stdout.write(f"Exported and flattened {count} PNG files into {repo / 'png'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
