# founder-portfolio

A Claude Code skill that turns one YAML data file into a 1-page A4 PDF founder portfolio in editorial magazine style. Encodes 13 design iterations (v6–v13, 65 PDFs) of typography research into a reproducible pipeline.

> Not a resume. **Editorial proof-of-work, in one page.**
> A traditional CV asks "where have you worked." A portfolio asks "what have you shipped."

---

## Install

```bash
git clone https://github.com/qjc-office/founder-portfolio ~/.claude/skills/founder-portfolio
bash ~/.claude/skills/founder-portfolio/scripts/bootstrap.sh
```

`bootstrap.sh` is idempotent. It creates a Python 3.10+ venv, installs pinned dependencies (`requirements.txt`), and probes for a Chrome/Chromium binary across macOS / Linux.

---

## Quick start

### 1. Render the bundled sample (Sangrok Jung profile)

```bash
~/.claude/skills/founder-portfolio/.venv/bin/python \
  ~/.claude/skills/founder-portfolio/scripts/render.py \
  --profile ~/.claude/skills/founder-portfolio/data/profile.yaml \
  --style all --out ~/Desktop/sangrok
```

Outputs five PDFs (~2–3 MB each) in `~/Desktop/`.

### 2. Render your own profile

Copy `data/profile.yaml` to your own `~/my-portfolio.yaml`, edit names / projects / clients / products / contact / social. Then:

```bash
.../render.py --profile ~/my-portfolio.yaml --style swiss-pure --out ~/me.pdf
```

Available styles: `swiss-pure` · `swiss-red` · `swiss-cream` · `swiss-navy` · `swiss-seal`. Or `--style all` for the full set.

### 3. As a Claude Code skill

Inside any Claude Code session, simply ask:

> "이력서 만들어줘. PDF로." · "Generate my founder portfolio in swiss-cream."

The skill description pattern-matches on `이력서 / 포트폴리오 / 프로필 / founder portfolio / executive resume / 1-pager` plus a PDF cue. The model resolves the right `profile.yaml` and runs `render.py` for you.

---

## Optional: AI portrait generation

If you want stylized headshots derived from your own face photo (5 presets — editorial / corporate / cinematic / monochrome / warm), see [docs/portrait-generation.md](docs/portrait-generation.md). This feature requires:

1. An OpenAI API key (https://platform.openai.com/api-keys) — each user provides their own
2. Explicit PIPA Article 28-8 consent (Korean Personal Information Protection Act) — see `privacy.md`
3. ~$0.20 in OpenAI credits for 5 portraits at ~$0.04 each (gpt-image-2 medium)

Quick flow:

```bash
# 1. Read the privacy notice and grant consent
.venv/bin/python scripts/consent.py grant

# 2. Generate 5 stylized portraits (OPENAI_API_KEY env var required)
export OPENAI_API_KEY=sk-...
.venv/bin/python scripts/generate_portrait.py \
  --source ~/me.jpg --out-dir ~/portraits

# 3. Optionally overlay hanja signature (Pillow + Nanum Myeongjo)
.venv/bin/python scripts/overlay_text.py \
  --source ~/portraits/editorial.png \
  --text 鄭常綠 \
  --position top-right \
  --out ~/portraits/editorial_signed.png

# 4. Update profile.yaml's `photo:` field, re-run render.py
```

To revoke consent and delete local data:

```bash
.venv/bin/python scripts/forget_me.py --yes
```

(OpenAI-side cached copies must be deleted via DSAR at https://privacy.openai.com or dsar@openai.com. The skill cannot reach into OpenAI's servers. OpenAI default retention is ≤30 days for abuse monitoring; input is not used for training since 2023-03.)

---

## Directory map

```
founder-portfolio/
├── SKILL.md                 # Description + pipeline (Claude reads this)
├── README.md                # This file (humans read this)
├── privacy.md               # PIPA Article 28-8 disclosure
├── data/profile.yaml        # Sample profile (Sangrok Jung)
├── templates/               # 5 Jinja2 magazine layouts
├── scripts/
│   ├── bootstrap.sh         # venv + dependency setup
│   ├── render.py            # Main: YAML → Jinja2 → Chrome → PDF
│   ├── generate_portrait.py # Optional: OpenAI gpt-image-2 (image-to-image)
│   ├── overlay_text.py      # Optional: Pillow hanja overlay
│   ├── consent.py           # PIPA consent grant/verify/revoke
│   ├── forget_me.py         # Right-to-deletion (PIPA Art. 36)
│   └── requirements.txt     # Pinned deps
├── assets/
│   ├── photos/              # 7 sample photos + your own
│   └── seals/               # 4 seal images (本人印 + 法人印)
├── references/              # Style catalog + schema docs
└── audit/                   # Independent security/policy audits
```

---

## Design philosophy

The 5 styles share a single 8-section data schema (Hero / Metrics / Quote / Selected Projects / Clients of Record / Self-Operated Products / Background trajectory / Colophon). The Jinja2 templates only differ in CSS — typography, spacing, and accent color. This means:

- **One profile.yaml drives many PDFs.** Update once, regenerate everywhere.
- **Style is a skin, not a fork.** New styles can be added without touching data.
- **Korean + Latin typography is first-class.** Pretendard, Nanum Myeongjo, EB Garamond, and Source Serif Pro are all included.

See `references/style-catalog.md` for the full 35-style reference (v6–v13) and `references/section-rationale.md` for why each section exists.

---

## Audits

Every claim in this README is backed by an independent audit:

- `audit/34_plugins_spec.md` — Why this stays a Skill (not a Plugin) for now
- `audit/35_image_pricing.md` — Provider comparison (fal.ai vs Imagen vs OpenAI)
- `audit/36_mvp_audit.md` — Code-quality review (HIGH/MEDIUM/LOW findings)
- `audit/37_security.md` — Threat model + sanitization choices
- `audit/B_codex_2nd_opinion.md` — Cross-model second opinion (gpt-5)
- `audit/C_policy_xverify.md` — PIPA + GDPR compliance verification
- `audit/00_synthesis_v2.md` — Final decisions, risks accepted

---

## License

MIT (template — adjust before redistribution).
