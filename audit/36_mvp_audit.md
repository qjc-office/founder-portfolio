# Task 36 — MVP Code Quality Audit (verdict: SHIP_WITH_FIXES)

> Reviewed: 2026-05-05 | Scope: code quality + runtime bugs (security covered in audit/37_security.md)
> Auditor: code-reviewer agent

---

## TL;DR

The pipeline is structurally sound and has produced working PDFs (5 styles, 2.3–3.0 MB) across 13 design iterations — that is real validation. The core loop (YAML → Jinja2 → Chrome headless → PDF) is solid. However, there are two blockers that will hit any first-time external user: Chrome is macOS-only with a hardcoded path, and `--style all` stops entirely on the first style failure. Five MEDIUM-tier issues affect robustness in common edge cases (name with three words, empty clients list, missing `seal_legal`, Linux deployment). No zombies, no secret leaks, no data mutation bugs.

---

## Findings (severity-tagged)

### CRITICAL — must fix before any external user

None. (Security issues tracked in audit/37_security.md.)

---

### HIGH — must fix in week 1

**[HIGH-1] Chrome hardcoded to macOS path — Linux/CI silently fails**
File: `scripts/render.py:43`, `scripts/bootstrap.sh:12–18`

```python
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

bootstrap.sh checks `[[ ! -x "$CHROME" ]]` and exits 1 with a useful error, but `render.py` never re-checks the binary at startup — it just passes the path to subprocess. On Linux the path doesn't exist, subprocess raises `FileNotFoundError`, and the traceback is raw Python with no user-facing message.

Fix: Add a `shutil.which` probe in `render.py` before `chrome_render_pdf` is called. Ordered fallback: `google-chrome`, `chromium-browser`, `chromium`, then the macOS hardcoded path. Print a clear error if none found.

```python
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium-browser",
    "chromium",
]

def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).is_file() or shutil.which(c):
            return c
    print("[render] ERROR: Chrome/Chromium not found. Install Google Chrome.", file=sys.stderr)
    sys.exit(1)
```

---

**[HIGH-2] `--style all` is aborted by first failure, not continued**
File: `scripts/render.py:261`

The `render_one` call inside the `for style in styles` loop calls `sys.exit(1)` (via `chrome_render_pdf`) on any Chrome failure. If `swiss-red` fails for any reason (e.g. font CDN timeout on first run), styles `swiss-cream`, `swiss-navy`, `swiss-seal` are never attempted. The user sees one PDF instead of five with no explanation of which styles succeeded.

Fix: Wrap `render_one` in a try/except in the `--style all` loop, collect failures, and continue. Report summary at end.

```python
failures: list[str] = []
for style in styles:
    try:
        outputs.append(render_one(data, style, pdf_path, tmp_dir))
    except SystemExit:
        failures.append(style)
        print(f"[render] WARNING: style '{style}' failed, continuing.", file=sys.stderr)
if failures:
    print(f"[render] SUMMARY: {len(failures)} style(s) failed: {', '.join(failures)}", file=sys.stderr)
    return 1 if len(failures) == len(styles) else 0
```

Note: this requires refactoring `chrome_render_pdf` to `raise RuntimeError` instead of calling `sys.exit`.

---

### MEDIUM — fix in next sprint

**[MEDIUM-1] `name.display` split assumes exactly two words — crashes on "Sangrok T. Jung"**
File: All 5 templates, e.g. `swiss-pure.html.j2:141`

```jinja2
<h1 class="hero-name"><b>{{ name.display.split(' ')[0] }}</b><br>{{ name.display.split(' ')[1] }}<span class="han">{{ name.hanja }}</span></h1>
```

`name.display.split(' ')[1]` raises `IndexError` if display name is a single word (e.g. "Sangrok"), and silently drops middle/last name parts for three-word names (e.g. "Sangrok T Jung" renders as "Sangrok" + "T", dropping "Jung"). This Jinja2 error propagates as a Python `UndefinedError` or index error — the HTML file is written with an empty/broken hero section and Chrome renders a corrupted PDF.

Fix: Use `name.first` / `name.last` fields in the schema, or Jinja2's `split` with a default:
```jinja2
{% set parts = name.display.split(' ') %}
<b>{{ parts[0] }}</b><br>{{ parts[1:] | join(' ') }}
```

---

**[MEDIUM-2] `swiss-seal` renders broken if `seal_legal` key is absent**
File: `scripts/render.py:48–61` (REQUIRED_KEYS), `templates/swiss-seal.html.j2:237`

`seal_legal` is NOT in `REQUIRED_KEYS`. The template uses `{{ seal_legal }}` (line 237) without a default. If a user customizes `profile.yaml` for their own data and omits `seal_legal`, Chrome receives an empty `src=""` attribute, showing a broken image icon in the signature row. The PDF renders but looks broken. The warning in `resolve_assets_in_data` only fires if the key exists but points to a missing file — a fully absent key produces no warning.

Fix option A: Add `seal_legal` to `REQUIRED_KEYS` only when style is `swiss-seal`.
Fix option B (cleaner): Jinja2 fallback: `{{ seal_legal | default('') }}`, and in CSS add `img:not([src]) { display: none }`.

---

**[MEDIUM-3] Chrome subprocess exit code is not checked**
File: `scripts/render.py:158`

```python
proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
```

The return value of `proc.returncode` is never read. Chrome headless exits non-zero on GPU errors and some Wayland/display configurations even when it successfully produces a PDF. Conversely, it can exit 0 but produce a corrupt/empty PDF. The current code only checks file size, which is a reasonable proxy, but a non-zero returncode should at least be logged as a WARNING to assist debugging.

Fix: After `subprocess.run`, add:
```python
if proc.returncode != 0:
    print(f"[render] WARNING: Chrome exited with code {proc.returncode}", file=sys.stderr)
```

---

**[MEDIUM-4] `bootstrap.sh` venv idempotency check may fail on Python minor version upgrade**
File: `scripts/bootstrap.sh:20`

```bash
if [[ -x "$VENV/bin/python" ]] && "$VENV/bin/python" -c "import jinja2, yaml, PIL" 2>/dev/null; then
```

If the user upgrades Python 3.12 → 3.13, the old venv's `bin/python` symlink still resolves but the compiled C extensions (PyYAML, Pillow) may be incompatible. The idempotency check passes (the old binary imports work), but the actual `render.py` invoked by `$VENV/bin/python3` will fail with `ImportError` at runtime — the same binary `pip` would install to the wrong interpreter.

Fix: Add a version check. The `.venv/pyvenv.cfg` contains `version = 3.X.Y`. Compare it against `$PYTHON --version` before skipping re-creation.

```bash
if [[ -x "$VENV/bin/python" ]] && "$VENV/bin/python" -c "import jinja2, yaml, PIL" 2>/dev/null; then
  VENV_VER=$("$VENV/bin/python" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  SYS_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  if [[ "$VENV_VER" == "$SYS_VER" ]]; then
    echo "[bootstrap] venv ready: $VENV"
    exit 0
  fi
  echo "[bootstrap] Python version mismatch ($VENV_VER vs $SYS_VER), recreating venv..."
fi
```

---

**[MEDIUM-5] `collect.py` `--refresh` flag documented in SKILL.md but `--enrich-from-customer-index` is the actual flag name**
File: `SKILL.md:78`, `scripts/collect.py:9`

SKILL.md pipeline step [2] documents the call as:
```
collect.py --enrich-from-customer-index
```

But the `--refresh` flag mentioned in SKILL.md line 4 description (`--refresh` flag) does not exist in collect.py's argparse at all. A user who runs `/founder-portfolio --refresh` will get no error and no data enrichment — collect.py is a no-op stub with any flag set, but the discrepancy between docs and implementation creates confusion.

Fix: Either (a) add `--refresh` as an alias for `--enrich-from-customer-index` in collect.py, or (b) remove `--refresh` from SKILL.md until the flag is implemented.

---

### LOW — nice-to-have

**[LOW-1] `autoescape=False` is correct but underdocumented for future contributors**
File: `scripts/render.py:184`

The comment `# YAML fields contain raw HTML (e.g., <b>...</b>)` is accurate and the decision is sound. But `| safe` is sprinkled across templates for `lead`, `quote.text`, `m.num`, `p.desc`, `c.name`, `prod.desc`. `m.num` (`"1,000+"`) has no HTML — `| safe` there is harmless but unnecessary and may surprise a contributor who thinks it implies untrusted input. This is a docs issue, not a bug.

Fix: Add a one-liner in render.py and in references/profile-schema.md: "Fields marked `| safe` are expected to contain `<b>`, `<em>` markup. Other fields do not need `| safe`."

**[LOW-2] `--no-open` help text says "Don't auto-open PDF on macOS" — actually already guarded by `platform.system() == "Darwin"`**
File: `scripts/render.py:215`, `render.py:263`

The flag is well-implemented — Linux users don't need it because `platform.system()` already gates the `open` call. The help text should say "Suppress auto-open (macOS only; no-op on other platforms)" to avoid confusion.

**[LOW-3] `tempfile.mkdtemp` cleanup always succeeds but is never logged**
File: `scripts/render.py:270`

`shutil.rmtree(tmp_dir, ignore_errors=True)` silently swallows cleanup failures. On a read-only filesystem or NFS mount this leaves temp files behind. Low severity because `ignore_errors=True` is appropriate here, but a debug-level log would help.

**[LOW-4] `emphasize_indices` out-of-range is silently ignored**
File: All templates, `background.steps` loop

If `emphasize_indices: [5, 6]` but `background.steps` only has 4 entries, Jinja2's `loop.index0 in emphasize_indices` never matches — no error, no accent, no warning. This is acceptable behavior (graceful degradation) but the YAML schema documentation does not document this edge case.

---

## Cross-cutting observations

**Mutation in data pipeline.** `resolve_assets_in_data` modifies `data` in place (line 133: `data[key] = resolve_asset_path(...)`). The docstring says "Convert... to absolute file:// URIs" but the return value is also used as an immutable profile. This is the project's only violation of the golden-principles immutability rule. It does not cause bugs in the current single-pass flow, but will if `data` is ever reused (e.g., if `--style all` is refactored to pass data per style). Fix: `return {**data, key: ...}` or deep copy first.

**No tempdir cleanup on partial `--style all` failure.** If `render_one` calls `sys.exit(1)` mid-loop (current behavior), the `finally: shutil.rmtree` in `main` still runs because `sys.exit` raises `SystemExit` which propagates through `finally`. This is actually correct Python behavior — cleanup happens even on exit. Credit where due.

**collect.py is a documented stub and nothing more.** The `--enrich-from-customer-index` flag is a no-op that prints a TODO and exits 0. SKILL.md's pipeline step [2] says "optionally enrich" which accurately scopes it, but the `--refresh` keyword mentioned in the skill description (first line) does not correspond to any implemented behavior. Week 1 users who try to use data enrichment will get nothing. This is a scope issue, not a bug — but it will generate support questions.

---

## What works well

- **Path resolution is correct under arbitrary cwd.** `SKILL_DIR = Path(__file__).resolve().parent.parent` pins all relative paths to the skill directory regardless of where `render.py` is invoked. This is the right pattern and avoids the most common portability bug in single-file scripts.
- **YAML validation exits early with specific key names.** `validate_schema` prints the dotted path of the missing key and the reference schema path — users get an actionable error immediately.
- **`tempfile.mkdtemp` + `finally` cleanup is correct.** Temp HTML files do not leak even on failure.
- **`--style all` output naming is unambiguous.** Stripping `.pdf` suffix before appending `_<style>.pdf` prevents double-extension bugs like `out.pdf_swiss-red.pdf`.
- **Chrome timeout is set.** `timeout=60` on `subprocess.run` prevents indefinite hangs on font CDN stalls.
