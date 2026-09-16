#!/usr/bin/env python3
"""Create a self-contained Overleaf project archive."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "homework-overleaf.zip"
ZIP_TIMESTAMP = (2020, 1, 1, 0, 0, 0)

EXCLUDED_ROOTS = {".git", ".github", ".venv", "scripts", "_minted"}
EXCLUDED_PATHS = {
    Path(".dockerignore"),
    Path(".gitattributes"),
    Path(".gitignore"),
    Path("AGENTS.md"),
    Path("Dockerfile"),
    Path("Makefile"),
    Path("docker-compose.yml"),
    Path("homework.pdf"),
    Path("latexmkrc"),
    Path("showcase.pdf"),
    Path("showcase.tex"),
    Path("theme/pygments"),
}
EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".d2",
    ".fdb_latexmk",
    ".fls",
    ".listing",
    ".lof",
    ".log",
    ".lot",
    ".out",
    ".pyc",
    ".pyg",
    ".pygstyle",
    ".pygtex",
    ".run.xml",
    ".synctex.gz",
    ".toc",
}

LATEXMKRC = """# Use LuaLaTeX for fontspec when this archive is built locally.
# Overleaf's compiler must still be selected in the project settings.
$pdf_mode = 1;
$dvi_mode = 0;
$postscript_mode = 0;
$pdflatex = 'lualatex %O %S';
$lualatex = 'lualatex %O %S';
"""


def is_excluded(path: Path, output: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path in {output, output.with_suffix(output.suffix + ".tmp")}:
        return True
    if relative.parts[0] in EXCLUDED_ROOTS:
        return True
    if any(relative == excluded or excluded in relative.parents
           for excluded in EXCLUDED_PATHS):
        return True
    if path.name.startswith("_minted") or path.name.endswith(
        "-luamml-mathml.html"
    ):
        return True
    if path.name == ".gitkeep":
        return True
    return any(path.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)


def source_files(output: Path) -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and not is_excluded(path, output)
    ]


def pygments_style() -> str:
    sys.path.insert(0, str(ROOT / "theme" / "pygments"))
    try:
        from pygments.formatters import LatexFormatter
        from rzstyle import RicardoLightStyle
    except ImportError as exc:
        raise SystemExit(
            "Pygments is required to create the Overleaf archive "
            "(Arch: pacman -S python-pygments)"
        ) from exc

    formatter = LatexFormatter(style=RicardoLightStyle, commandprefix="PYG")
    return formatter.get_style_defs().lstrip() + "\n"


def add_bytes(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, content, compresslevel=9)


def main() -> int:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    if output.parent != ROOT:
        raise SystemExit(
            "the Overleaf archive must be written in the repository root"
        )

    temporary = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        for path in source_files(output):
            add_bytes(archive, path.relative_to(ROOT).as_posix(), path.read_bytes())
        add_bytes(archive, "latexmkrc", LATEXMKRC.encode())
        add_bytes(
            archive,
            "_minted/rzstyle-light.style.minted",
            pygments_style().encode(),
        )

    temporary.replace(output)
    print(f">> overleaf: {output.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
