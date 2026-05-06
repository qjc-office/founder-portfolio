---
name: founder-portfolio
description: |
  Generate a 1-page A4 PDF founder portfolio (executive resume) in editorial magazine style — Swiss/New Yorker/HBR/Forbes/Princeton variants. Use when the user asks to create, build, generate, redesign, or improve a "이력서", "포트폴리오", "프로필", "founder portfolio", "executive resume", "프로필 PDF", "회사 소개 1장", "1-pager", "리더 소개서". The skill bundles 13 cycles (v6-v13, 65 designs) of editorial typography research into a single command. Output is a 1-page A4 PDF saved to the current working directory or a user-specified path. Triggers strongly on "이력서 만들어", "포트폴리오 PDF", "founder profile", "프로필 만들어 PDF로", or any combination of resume/profile/portfolio + PDF/디자인/A4.
---

# Founder Portfolio Skill

> A founder portfolio is not a resume — it is a 1-page editorial proof of work. A traditional CV asks "where have you worked"; a portfolio asks "what have you shipped." This skill encodes 13 design iterations into a reproducible pipeline: one YAML data file → many magazine-style PDFs.

## When to use

This skill triggers when the user wants a **professional, editorial-style 1-page profile PDF** — typically for:

- **Founder/executive bio** sent with a B2B proposal, speaker pitch, or media outreach
- **Replacement for a traditional resume** when the work itself is the credential (consultants, founders, public-facing creators)
- **Self-introduction packet** for advisory engagements, partnerships, board roles
- **Press kit one-pager** to send with interview requests

Do NOT use for:
- Standard ATS-friendly resumes → route to `resume-builder` (Reactive Resume schema)
- Multi-page company decks → use slide tools
- Email signatures or social bios → too short for this skill

## What it produces

A single-page A4 PDF (~2-3 MB) with this canonical 8-section structure (validated across 13 design iterations):

1. **Top bar** — brand mark + issue date
2. **Hero** — portrait + name (한자 병기) + role + lead paragraph
3. **Background trajectory** — education → career flow (no dates, just the arrow chain)
4. **Metrics** — 4 quantified proof points (students, audience, clients)
5. **Pull quote** — one-line positioning statement
6. **Selected Projects** — 5–10 named engagements with deliverable status
7. **Clients of Record** — 25–30+ matrix grouped by category
8. **Self-Operated Products** — 5–9 own product lines (founder signal)
9. **Colophon** — contact + SNS handles + seal/signature

## How to invoke

```
/founder-portfolio                          # default style (swiss-pure)
/founder-portfolio swiss-red                 # specific style
/founder-portfolio --all                     # all 5 styles in parallel
/founder-portfolio --catalog                 # list all available styles
/founder-portfolio --profile path/to.yaml    # alternative profile data
/founder-portfolio --output ~/Desktop/       # custom output dir
```

## Available styles (MVP — 5 Swiss variants)

All styles share the **same 12-column grid + Inter/Source Serif Pro typography + identical 8-section structure**. Only the accent color and subtle elements vary — this is intentional: a founder portfolio's authority comes from restraint, not decoration.

| ID | Name | Accent | When to pick it |
|----|------|--------|-----------------|
| `swiss-pure` | Swiss Pure | Black/white only | Universal default. Maximum readability |
| `swiss-red` | Swiss Red Accent | Single red hairline | Slight emphasis, retains restraint |
| `swiss-cream` | Swiss Cream | Black on beige #F5F0E4 | Magazine warmth, EB Garamond pairing |
| `swiss-navy` | Swiss Navy | Navy #0A2540 | B2B, finance, formal proposal context |
| `swiss-seal` | Swiss Korean Seal | Vermilion 朱印 + photo overlay | Korean institutional contexts, legal-adjacent |

For 30 additional editorial references (Forbes / TIME Cover / NYT / Penguin / 사대부 / etc.) see [references/style-catalog.md](references/style-catalog.md). These can be ported into templates on demand.

## Pipeline (the model executes this)

```
[1] Bootstrap (idempotent, ~5s if cached)
    bash <skill-dir>/scripts/bootstrap.sh
    → Creates .venv with Jinja2, PyYAML, Pillow
    → Verifies Chrome headless availability

[2] Data resolution (priority order)
    a. --profile <path>   → load that YAML
    b. ./profile.yaml      → if exists in cwd
    c. <skill-dir>/data/profile.yaml  → bundled default (Sangrok Jung)
    
    For QJC project context, optionally enrich:
    <venv>/python <skill-dir>/scripts/collect.py --enrich-from-customer-index
    (NOTE: collect.py is a stub in this MVP — Supabase/customer-index
     auto-enrichment is Phase 2. Today, edit profile.yaml by hand.)

[3] Render
    <venv>/python <skill-dir>/scripts/render.py \
      --profile <resolved-yaml> \
      --style <style-id> \
      --out <output-path>
    → Jinja2 fills template with profile data
    → Chrome headless rasterizes to A4 PDF
    → Output: <output-dir>/<name>_portfolio_<style>.pdf

[4] User notification
    → Print PDF path
    → If multiple styles, list all paths
    → Auto-open via `open <path>` on macOS unless --no-open
```

## Optional: AI portrait generation (OpenAI gpt-image-2)

If the user wants stylized headshots derived from their own face photo:

```
[A] Generate portraits (5 presets: editorial / corporate / cinematic / monochrome / warm)
    <venv>/python <skill-dir>/scripts/generate_portrait.py \
      --source <user-photo> \
      --out-dir <output-dir>
    → Reads OPENAI_API_KEY env var (user issues at https://platform.openai.com/api-keys)
    → Source photo uploaded via OpenAI Images Edit API (model=gpt-image-2)
    → ~$0.04 per image (medium quality), 5 presets × $0.04 = $0.20
    → Use --quality high only for print/signage (~$0.10-0.20/image)
    → Use --dry-run to preview prompts without calling OpenAI
    → Use --presets editorial,monochrome to subset

[B] Overlay hanja / name signature on a generated portrait
    <venv>/python <skill-dir>/scripts/overlay_text.py \
      --source <portrait.png> \
      --text "鄭常綠" \
      --position top-right \
      --out <signed-portrait.png>
    → Pillow + Nanum Myeongjo / Source Han Serif KR (auto-detected)
    → Default: top-right, small (Wallpaper magazine tone)
    → Other presets: bottom-left (사대부), center (인감 watermark)
    → Even with gpt-image-2's 90%+ hanja accuracy, a deterministic local overlay
      is preferred for legal-grade documents.

[C] Use generated portraits in render
    Update profile.yaml's `photo:` field to point at the new portrait,
    then re-run `render.py` as in step [3].
```

## PIPA / privacy posture (Korean PIPA Article 28-8)

Face photos are biometric data under PIPA Article 23 (sensitive personal information).
When the user invokes `generate_portrait.py` for the first time, the skill MUST:

1. Display a separate, explicit consent dialog covering:
   - Recipient: OpenAI, OpCo LLC (privacy@openai.com)
   - Country: United States (Azure US datacenters)
   - Purpose: AI image generation (gpt-image-2 image-to-image)
   - Retention: ≤ 30 days (OpenAI default abuse monitoring; not used for training since 2023-03)
   - Right to refuse: yes (cannot use feature without consent)
2. Record consent timestamp + version to `~/.claude/skills/founder-portfolio/.consent.json`
3. Provide a deletion-request channel (re-runs delete `.consent.json` and any cached portraits;
   server-side copies require DSAR via https://privacy.openai.com)

Implemented in Phase 3 (see `privacy.md` v2.0 + `scripts/consent.py`).
The supported flow is **self-use only**: the user is the data subject themselves
and is using their own OpenAI API key. Uploading other people's photos
without their explicit consent violates OpenAI usage policies and is the
user's sole responsibility.

## Why this design (the why behind every choice)

**Why YAML, not JSON?** YAML lets the user write multi-line bullet text without escaping. A founder profile has long descriptions and Korean text — JSON would force `\n` everywhere.

**Why Chrome headless, not weasyprint?** v6-v13 testing showed weasyprint fails on `display:grid` (the 12-col Swiss grid), `font-feature-settings`, and Korean kerning. Chrome headless with `--print-to-pdf` matches the exact rendering of the HTML preview, which is what 13 iterations were tuned against. report-designer uses weasyprint for a different need (server reports); founder-portfolio specifically requires print-fidelity.

**Why one shared 8-section template across all styles?** Information architecture is the hard part; visual variation is cheap. Forcing every style into the same skeleton means switching styles is a one-line change, and the data file stays portable.

**Why a "Background trajectory" line instead of a dated CV?** Dated career sections are the easiest target for "ex-Anthropic" credential fraud. A flow line ("백제예술대 → 엔코아 → 경남대 빅데이터 연구원 → Founder, QJC") communicates trajectory without inviting forensic interrogation. The proof is in the projects/clients sections.

**Why Korean hanja name?** Many Korean B2B and institutional contexts treat 한자 병기 as a marker of formality. The skill keeps it optional — set `name.hanja: ""` in YAML to omit.

**Why max 1 page?** The format is a constraint that forces editing. If it does not fit on A4, the priority list is wrong, not the design.

## Customizing for a different person

```yaml
# profile.yaml — minimum viable schema
name:
  display: "Sangrok Jung"
  korean: "정상록"
  hanja: "鄭常綠"        # optional, omit to skip
role: "Founder & CEO, Quantum Jump Club"
location: "Pangyo, Korea"
established: 2024
photo: "assets/photos/p2_gq_charcoal.png"  # relative to skill or absolute
seal: "assets/seals/seal_hanja_round.png"

lead: |
  이력 한 장이 아닌 공개된 결과물로 검증되어 온 컨설턴트.
  Claude Code 하네스를 직접 운영하는 30곳+ 자문 파트너이자,
  누적 1,000명 이상의 교육 수강생을 배출한 부티크의 창립자.

background:                    # no dates, just the arrow flow
  - "백제예술대 미디어음악과 (작곡)"
  - "엔코아 플레이데이터 커뮤니티 운영 총괄"
  - "경남대 빅데이터 연구원 (KDATA 빅리더 사업)"
  - "Founder, Quantum Jump Club"

metrics:
  - { num: "1,000+", label: "Total Students" }
  - { num: "29K+", label: "YouTube · @qjc_qjc" }
  - { num: "26K+", label: "Threads · @qjc.ai" }
  - { num: "30+", label: "Clients of Record" }

quote:
  text: "Claude Code 하네스를 직접 운영하는 컨설턴트는 흔치 않습니다. 이력 한 장으로 의심받는 시대, 저는 공개된 결과물로 검증되어 왔습니다."
  attribution: "Sangrok Jung · Founder & CEO"

projects:                      # 5-10 entries
  - { typ: "Samsung", name: "GenAI L4", desc: "..." }
  # ...

clients:                       # 25-30+ entries, 4-col matrix
  - { typ: "Enterprise", name: "삼성전자 · GenAI L4" }
  # ...

products:                      # 5-9 entries
  - { num: "01", name: "특이점 빌더스", desc: "..." }
  # ...

contact:
  mobile: "010-8216-8366"
  email: "sangrok@quantumjumpclub.com"
  website: "qjc.app"
  social:
    youtube: "youtube.com/@qjc_qjc"
    instagram: "instagram.com/qjc.ai"
    linkedin: "linkedin.com/in/sangrok-jung"
    threads: "threads.com/@qjc.ai"
```

For the full schema with all optional fields, see [references/profile-schema.md](references/profile-schema.md).

## Failure modes and recovery

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Chrome PDF blank or 0 KB | Profile YAML missing required key | `render.py` validates schema and prints which key is missing |
| Hanja shows as boxes | Nanum Myeongjo font not in Google Fonts CDN cache | Templates load via `<link rel="stylesheet">` — first run requires network |
| Photo path 404 | Path resolution mismatch | render.py converts relative paths → file:// URIs before passing to Chrome |
| Sections overflow A4 page | Too many projects/clients | Limit projects ≤ 10, clients ≤ 32, products ≤ 9. Skill warns if exceeded |

## Extending: adding a new style

1. Copy a base template: `cp templates/swiss-pure.html.j2 templates/my-style.html.j2`
2. Modify only `--accent`, fonts, or hairline elements — keep the 8-section grid intact
3. Add to `styles` list in `scripts/render.py` STYLES dict
4. Test: `/founder-portfolio my-style`

## References

- [references/profile-schema.md](references/profile-schema.md) — full YAML schema
- [references/style-catalog.md](references/style-catalog.md) — 35 editorial references (Forbes/NYT/Penguin/etc.)
- [references/section-rationale.md](references/section-rationale.md) — why each of the 8 sections exists, with research notes from 13 iterations

## Related skills

- `resume-builder` — ATS resumes (Reactive Resume schema). Different format, different audience
- `weekly-pdf` — weekly business KPI PDF. Same Chrome rendering pattern, different content
- `awesome-design-md` — 58 brand DESIGN.md references. Reuses the editorial vocabulary
- `report-designer` — weasyprint reports. Skip for founder portfolio (grid incompatible)
