#!/usr/bin/env python3
"""Render YAML profile + Jinja2 template → A4 PDF via Chrome headless.

Usage:
    render.py --profile path/to/profile.yaml --style swiss-pure --out /tmp/out.pdf
    render.py --profile path/to/profile.yaml --style all --out /tmp/sangrok

Pipeline:
1. Load YAML profile (yaml.safe_load).
2. Validate required keys + style-specific keys (e.g. seal_legal for swiss-seal).
3. Derive name.first/last from name.display (templates use these).
4. Bleach-clean every string field with allow-list (<b><em><strong><br><span>).
5. Resolve photo/seal/seal_legal paths to file:// URIs.
6. Render Jinja2 with autoescape=True (sanitized fields can still use |safe).
7. Run Chrome headless (cross-platform finder) → PDF.
8. For --style all: render every style independently; one failure does not
   abort the rest.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
    import bleach
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    from markupsafe import Markup
except ImportError as e:
    print(f"[render] missing dependency: {e}; run scripts/bootstrap.sh", file=sys.stderr)
    sys.exit(2)


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "templates"

ALL_STYLES = ["swiss-pure", "swiss-red", "swiss-cream", "swiss-navy", "swiss-seal"]
DEFAULT_STYLE = "swiss-pure"

# Required keys for ALL styles.
REQUIRED_KEYS: list[tuple[str, ...]] = [
    ("name", "display"),
    ("role",),
    ("location",),
    ("lead",),
    ("background", "steps"),
    ("metrics",),
    ("quote", "text"),
    ("projects",),
    ("clients",),
    ("products",),
    ("contact", "email"),
    ("social",),
]

# Style-specific extra keys (only required when that style is rendered).
STYLE_REQUIRED: dict[str, list[tuple[str, ...]]] = {
    "swiss-seal": [("seal_legal",)],
}

# Bleach allow-list. Only these tags survive sanitization; everything else
# (script, link, iframe, on*= handlers, javascript: URIs) is stripped.
ALLOWED_TAGS = ["b", "em", "i", "strong", "br", "span"]
ALLOWED_ATTRS: dict[str, list[str]] = {"span": ["class"]}


# ─────────────────────────── Chrome detection ───────────────────────


def find_chrome() -> str:
    """Locate a Chrome/Chromium binary across macOS, Linux, and CI environments.

    Probe order is intentional: prefer Google Chrome (matches v13 baseline
    rendering), fall back to chromium variants. Raises FileNotFoundError with
    actionable guidance instead of crashing deeper in the pipeline.
    """
    candidates: list[str | None] = []
    system = platform.system()
    if system == "Darwin":
        candidates.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        candidates.append("/Applications/Chromium.app/Contents/MacOS/Chromium")
    candidates.extend([
        os.environ.get("CHROME_BIN"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome"),
    ])
    for path in candidates:
        if path and Path(path).exists():
            return path
    raise FileNotFoundError(
        "Chrome/Chromium not found. Install Google Chrome, set $CHROME_BIN, "
        "or `brew install chromium` / `apt install chromium-browser`."
    )


# ─────────────────────────── Validation ─────────────────────────────


def validate_schema(
    data: dict[str, Any], profile_path: Path, styles: list[str]
) -> None:
    """Check required keys; include style-specific keys for selected styles."""
    required = list(REQUIRED_KEYS)
    for style in styles:
        required.extend(STYLE_REQUIRED.get(style, []))

    for path in required:
        cur: Any = data
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                dotted = ".".join(path)
                print(
                    f"[render] Profile schema error: required key '{dotted}' missing in {profile_path}.",
                    file=sys.stderr,
                )
                print(
                    f"[render] See {SKILL_DIR / 'data' / 'profile.yaml'} for reference schema.",
                    file=sys.stderr,
                )
                sys.exit(2)
            cur = cur[key]


def warn_lengths(data: dict[str, Any]) -> None:
    """Soft warnings for lengths that may overflow A4."""
    metrics = data.get("metrics") or []
    if len(metrics) != 4:
        print(f"[render] WARNING: metrics has {len(metrics)} entries (templates expect 4).", file=sys.stderr)
    projects = data.get("projects") or []
    if len(projects) > 10:
        print(f"[render] WARNING: projects has {len(projects)} entries (>10 may overflow A4).", file=sys.stderr)
    clients = data.get("clients") or []
    if len(clients) > 32:
        print(f"[render] WARNING: clients has {len(clients)} entries (>32 may overflow grid).", file=sys.stderr)
    products = data.get("products") or []
    if len(products) > 9:
        print(f"[render] WARNING: products has {len(products)} entries (>9 may overflow 3×3).", file=sys.stderr)


# ─────────────────────────── Sanitization ───────────────────────────


# Keys whose values are paths or contact strings — DO NOT sanitize these
# (bleach is for HTML; paths legitimately contain '/' and ':').
PATH_KEYS = {"photo", "seal", "seal_legal"}


def sanitize_html_recursive(obj: Any, current_key: str | None = None) -> Any:
    """Bleach-clean every string in the data tree using the allow-list.

    Why recursive: profiles contain nested lists (projects[].desc, clients[].name)
    where any field can carry attacker-controlled HTML (<script>, <link href=
    "file:///etc/passwd">). Sanitizing once at ingest is simpler and stricter
    than per-template safe-filter overrides.

    Path-typed keys (photo/seal/seal_legal) bypass cleaning so URI separators
    and absolute paths survive intact.
    """
    if isinstance(obj, str):
        if current_key in PATH_KEYS:
            return obj  # paths bypass HTML sanitization
        return bleach.clean(obj, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    if isinstance(obj, dict):
        return {k: sanitize_html_recursive(v, current_key=k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_html_recursive(v, current_key=current_key) for v in obj]
    return obj


# ─────────────────────────── Path resolution ────────────────────────


def resolve_asset_path(value: str, base_dir: Path) -> str:
    """Resolve a relative asset path against base_dir; absolute paths pass through."""
    p = Path(value)
    if not p.is_absolute():
        p = (base_dir / p).resolve()
    if not p.exists():
        print(f"[render] WARNING: asset not found: {p}", file=sys.stderr)
    return p.as_uri()


def resolve_assets_in_data(data: dict[str, Any]) -> dict[str, Any]:
    """Convert photo/seal/seal_legal fields to absolute file:// URIs."""
    for key in ("photo", "seal", "seal_legal"):
        if key in data and data[key]:
            data[key] = resolve_asset_path(data[key], SKILL_DIR)
    return data


# ─────────────────────────── Name derivation ────────────────────────


def derive_name_parts(data: dict[str, Any]) -> dict[str, Any]:
    """Split name.display into first / last for template hero markup.

    Templates currently render `<b>{{ first }}</b><br>{{ last }}`. The naive
    split('  ')[1] crashes on single-word display names ("Madonna") and
    silently drops surnames on three-word names ("Jose Maria Aznar"). This
    helper assigns first = first token, last = remainder (joined).
    """
    name = data.get("name", {})
    display = (name.get("display") or "").strip()
    if not display:
        return data
    tokens = display.split()
    if "first" not in name:
        name["first"] = tokens[0]
    if "last" not in name:
        name["last"] = " ".join(tokens[1:]) if len(tokens) > 1 else ""
    data["name"] = name
    return data


# ─────────────────────────── Rendering ──────────────────────────────


class RenderError(RuntimeError):
    """Raised when one PDF fails; allows --style all to continue with the rest."""


def chrome_render_pdf(html_path: Path, pdf_path: Path, chrome_bin: str) -> None:
    """Run Chrome headless to convert HTML → PDF. Raises RenderError on failure.

    This used to call sys.exit(1) — that aborted --style all on first failure.
    Now: raise RenderError so the caller can collect failures and continue.
    """
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-file-access-from-files",  # blocks file:// XHR exfiltration
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        "--virtual-time-budget=8000",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise RenderError(f"Chrome timed out (>60s) on {html_path.name}")

    if proc.returncode != 0:
        # Chrome can produce a valid-looking PDF even with a non-zero exit
        # (Wayland/GPU warnings on Linux). Log but don't fail unless size also fails.
        snippet = (proc.stderr or "").strip().splitlines()[:3]
        print(f"[render] WARNING: Chrome returncode={proc.returncode}: {' / '.join(snippet)}", file=sys.stderr)

    size = pdf_path.stat().st_size if pdf_path.exists() else 0
    if not pdf_path.exists() or size < 100 * 1024:
        stderr_tail = (proc.stderr or "").strip()
        if stderr_tail:
            print(f"[render] Chrome stderr:\n{stderr_tail}", file=sys.stderr)
        raise RenderError(f"PDF too small or missing (size={size} bytes, html={html_path.name})")


def render_one(
    data: dict[str, Any], style: str, out_path: Path, tmp_dir: Path, chrome_bin: str
) -> Path:
    """Render a single style → PDF, return absolute PDF path.

    Raises RenderError on failure (caller decides whether to continue).
    """
    template_name = f"{style}.html.j2"
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise RenderError(f"template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        # autoescape ON. Fields are pre-sanitized (bleach allow-list); |safe in
        # templates marks them as "already-cleaned HTML, don't re-escape" which
        # is now safe because cleaning happened at ingest, not at render.
        autoescape=select_autoescape(default_for_string=True, default=True),
    )
    template = env.get_template(template_name)
    html_str = template.render(**data, d=data, profile=data, style=style)

    html_path = tmp_dir / f"{style}.html"
    html_path.write_text(html_str, encoding="utf-8")

    pdf_abs = out_path.resolve()
    chrome_render_pdf(html_path, pdf_abs, chrome_bin)

    size_kb = pdf_abs.stat().st_size // 1024
    print(f"✓ Rendered: {pdf_abs} ({size_kb} KB, style={style})")
    return pdf_abs


# ─────────────────────────── Main ───────────────────────────────────


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render founder portfolio PDFs.")
    p.add_argument("--profile", required=True, type=Path, help="Path to profile YAML")
    p.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        help=f"Style id: {', '.join(ALL_STYLES)}, or 'all'",
    )
    p.add_argument("--out", required=True, type=Path, help="Output PDF path (or stem if --style all)")
    p.add_argument("--no-open", action="store_true", help="Don't auto-open PDF on macOS")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    profile_path = args.profile if args.profile.is_absolute() else (Path.cwd() / args.profile).resolve()
    if not profile_path.exists():
        print(f"[render] ERROR: profile not found: {profile_path}", file=sys.stderr)
        return 2

    raw = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        print(f"[render] ERROR: profile YAML did not parse to a mapping: {profile_path}", file=sys.stderr)
        return 2

    if args.style == "all":
        styles = ALL_STYLES
    elif args.style in ALL_STYLES:
        styles = [args.style]
    else:
        print(
            f"[render] ERROR: unknown style '{args.style}'. Choose from: {', '.join(ALL_STYLES)}, all",
            file=sys.stderr,
        )
        return 2

    validate_schema(raw, profile_path, styles)
    warn_lengths(raw)

    # Sanitize HTML in every string field (allow-list), then resolve asset
    # paths and derive name.first/last. Order matters: sanitize BEFORE asset
    # resolution so the path strings (photo/seal/seal_legal) are excluded by
    # PATH_KEYS but file:// URIs we generate are not subjected to bleach.
    data = sanitize_html_recursive(raw)
    data = resolve_assets_in_data(data)
    data = derive_name_parts(data)

    try:
        chrome_bin = find_chrome()
    except FileNotFoundError as e:
        print(f"[render] ERROR: {e}", file=sys.stderr)
        return 2

    tmp_dir = Path(tempfile.mkdtemp(prefix="founder-portfolio-"))
    outputs: list[Path] = []
    failures: list[tuple[str, str]] = []
    try:
        for style in styles:
            if args.style == "all":
                stem = args.out
                if stem.suffix.lower() == ".pdf":
                    stem = stem.with_suffix("")
                pdf_path = stem.parent / f"{stem.name}_{style}.pdf"
            else:
                pdf_path = args.out
            try:
                outputs.append(render_one(data, style, pdf_path, tmp_dir, chrome_bin))
            except RenderError as e:
                failures.append((style, str(e)))
                print(f"✗ FAILED: style={style}: {e}", file=sys.stderr)
                # continue to next style — the whole point of fix HIGH-2

        if failures:
            print(
                f"\n[render] {len(failures)} style(s) failed, {len(outputs)} succeeded.",
                file=sys.stderr,
            )

        if not args.no_open and platform.system() == "Darwin":
            for path in outputs:
                try:
                    subprocess.run(["open", str(path)], check=False)
                except FileNotFoundError:
                    pass
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Exit code: 0 if at least one PDF succeeded, 1 if all failed.
    return 0 if outputs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
