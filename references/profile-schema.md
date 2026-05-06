# Profile Schema Reference

> The full YAML schema documented field-by-field. Every field in `data/profile.yaml` is listed here with its type, requirement, validation rules, and an example value. The schema is intentionally flat where possible — YAML's strength is multiline strings and lists, and the renderer relies on that.

---

## Top-level layout

```yaml
name:        # object — see § 1
role:        # string — see § 2
location:    # string — see § 2
established: # int    — see § 2
issue_date:  # string — see § 2
photo:       # string — see § 3
photo_caption:
seal:
seal_legal:
brand_tag:   # string — see § 4
lead:        # string (multiline) — see § 5
background:  # object — see § 6
metrics:     # list of {num, label} — see § 7
quote:       # object — see § 8
projects:    # list of {typ, name, desc} — see § 9
clients:     # list of {typ, name} — see § 10
products:    # list of {num, name, desc} — see § 11
contact:     # object — see § 12
social:      # object — see § 13
```

---

## § 1 — `name` (object, required)

The headline identity block. Rendered in the hero section.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `name.display` | string | ✅ Required | 1–40 chars, Latin script preferred for the masthead line | `"Sangrok Jung"` |
| `name.korean` | string | optional | 한글 only, 2–6 chars | `"정상록"` |
| `name.hanja` | string | optional | 한자 only, 2–6 chars. Set to empty string `""` to skip | `"鄭常綠"` |

**Note**: When `name.korean` and `name.hanja` are both present, the renderer formats them as `정상록 鄭常綠`. The hanja line is intended for Korean B2B / institutional formality; omit when sending to non-Korean audiences.

---

## § 2 — Identity scalars (strings/int, required)

| Field | Type | Required | Validation | Example |
|-------|------|----------|------------|---------|
| `role` | string | ✅ Required | 1 line, 10–80 chars. Format: `"Title, Company"` | `"Founder & CEO, Quantum Jump Club"` |
| `location` | string | ✅ Required | 1 line, city + country | `"Pangyo, Korea"` |
| `established` | int | ✅ Required | 4-digit year. Used in colophon: `Est. 2024` | `2024` |
| `issue_date` | string | ✅ Required | ISO `YYYY-MM-DD`. Rendered top-bar | `"2026-05-01"` |

---

## § 3 — Visual assets (strings)

| Field | Type | Required | Validation | Example |
|-------|------|----------|------------|---------|
| `photo` | string | ✅ Required | Path relative to skill-dir or absolute. PNG/JPG. Recommended 4:5 portrait, ≥1200px wide | `"assets/photos/p2_gq_charcoal.png"` |
| `photo_caption` | string | optional | 1 line, italic in some styles | `"Photographed in Pangyo, May 2026."` |
| `seal` | string | optional | PNG with transparent background. Round seal, ≥400×400px. Used by `swiss-seal` style | `"assets/seals/seal_hanja_round.png"` |
| `seal_legal` | string | optional | 法人印 (corporate seal). Only required when style demands it | `"assets/seals/seal_company_qjc.png"` |

**Path resolution**: `render.py` converts relative paths to `file://` URIs before passing the rendered HTML to Chrome. Absolute paths (`/Users/...`) are also accepted. iCloud paths with spaces work — Jinja2 escapes them. URL paths (`https://...`) are not recommended (Chrome's `--print-to-pdf` may race against image loading).

---

## § 4 — `brand_tag` (string, optional)

A single editorial tagline rendered in the top bar next to the brand mark. Keep ≤30 chars.

| Type | Required | Example |
|------|----------|---------|
| string | optional | `"A founder portfolio."` |

If omitted, the top bar shows only the issue date and brand mark.

---

## § 5 — `lead` (string, required)

The hero-section lead paragraph. **Multiline string** — use YAML's `|` literal block.

| Type | Required | Validation | Example |
|------|----------|------------|---------|
| string (multiline) | ✅ Required | 80–250 chars, 2–4 lines | See below |

```yaml
lead: |
  이력 한 장이 아닌 공개된 결과물로 검증되어 온 컨설턴트.
  Claude Code 하네스를 직접 운영하는 30곳+ 자문 파트너이자,
  누적 1,000명 이상의 교육 수강생을 배출한 부티크의 창립자.
```

**Tone**: A single descriptive paragraph in the third person or first person. Avoid bullet points — the lead is prose.

---

## § 6 — `background` (object, required)

The trajectory line. **No dates** — only an arrow chain of stops.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `background.label` | string | optional | Default `"Background"`. Override for localization (`"이력"`) | `"Background"` |
| `background.steps` | list of string | ✅ Required | 3–6 entries. Each step is one institution + role | See below |
| `background.emphasize_indices` | list of int | optional | 0-indexed positions to render in accent color | `[2, 3]` |

```yaml
background:
  label: "Background"
  steps:
    - "백제예술대 미디어음악과 (작곡)"
    - "엔코아 플레이데이터 커뮤니티 운영 총괄"
    - "경남대 빅데이터 연구원 (KDATA 빅리더 사업)"
    - "Founder, Quantum Jump Club"
  emphasize_indices: [2, 3]
```

**Critical rule**: Do NOT add years/months to step strings. The whole point of trajectory-without-dates is to communicate path without inviting credential interrogation. Years belong in the colophon (`established`), not here.

---

## § 7 — `metrics` (list of objects, required)

Exactly **4 cards**. Each occupies 3 columns of the 12-col grid.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `metrics[].num` | string | ✅ Required | Quantified figure. Suffixes (`+`, `K`, `M`) ok. Max 8 chars | `"1,000+"` |
| `metrics[].label` | string | ✅ Required | One-line proof axis. 5–30 chars | `"Total Students"` |

```yaml
metrics:
  - { num: "1,000+", label: "Total Students" }
  - { num: "29K+",   label: "YouTube · @qjc_qjc" }
  - { num: "26K+",   label: "Threads · @qjc.ai" }
  - { num: "30+",    label: "Clients of Record" }
```

**Why 4 (not 3 or 5)**: 4 fits the 12-col grid evenly (3 cols each) and is the cognitive sweet spot — 3 looks sparse, 5+ creates a dashboard feel. The renderer rejects lists ≠ 4.

---

## § 8 — `quote` (object, required)

The pull-quote section. One positioning sentence.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `quote.text` | string | ✅ Required | 80–200 chars. Single sentence, italic in render | See below |
| `quote.attribution` | string | ✅ Required | `Name · Role, Company` format | `"Sangrok Jung · Founder & CEO, Quantum Jump Club"` |

```yaml
quote:
  text: "Claude Code 하네스를 직접 운영하는 컨설턴트는 흔치 않습니다. 이력 한 장으로 의심받는 시대, 저는 공개된 결과물로 검증되어 왔습니다."
  attribution: "Sangrok Jung · Founder & CEO, Quantum Jump Club"
```

---

## § 9 — `projects` (list of objects, required)

Selected engagements. **5–10 entries**. The renderer enforces ≤10.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `projects[].typ` | string | ✅ Required | Tag prefix shown above the name. Format: `"NN · Brand · Date"` recommended | `"02 · Kakao · 5/14"` |
| `projects[].name` | string | ✅ Required | Project headline (rendered bold). 4–25 chars | `"하네스 세미나"` |
| `projects[].desc` | string | ✅ Required | 1-line description. **HTML allowed** — `<b>...</b>` for emphasis. Use `|safe` filter is auto-applied | See below |

```yaml
projects:
  - typ: "02 · Kakao · 5/14"
    name: "하네스 세미나"
    desc: "<b>카카오</b> 사내 「하네스 엔지니어링 세미나」 · 제안서 v2 송부 · 2026.05.14 예정 (양나은 담당)."
```

---

## § 10 — `clients` (list of objects, required)

The Clients of Record matrix. **Exactly 32 entries** (4 columns × 8 rows fits A4 cleanly). Renderer warns at >32.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `clients[].typ` | string | ✅ Required | Category tag. Recommended set: `Enterprise / Public / University / EdTech / Publishing / Project / Venture / Strategy / Media` | `"Enterprise"` |
| `clients[].name` | string | ✅ Required | `Client · Engagement` format. Max 30 chars | `"삼성전자 · GenAI L4"` |

```yaml
clients:
  - { typ: "Enterprise", name: "삼성전자 · GenAI L4" }
  - { typ: "University", name: "한국예술종합학교 · KNUA" }
  # ... 32 total
```

---

## § 11 — `products` (list of objects, required)

Self-operated products. **Exactly 9 entries** (3 cols × 3 rows). This is the "founder signal" section.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `products[].num` | string | ✅ Required | Zero-padded index (`"01"`, `"02"`, ...) | `"01"` |
| `products[].name` | string | ✅ Required | Product line name. 4–20 chars | `"특이점 빌더스"` |
| `products[].desc` | string | ✅ Required | 1-line description. HTML allowed (`<b>...</b>`) | See below |

```yaml
products:
  - num: "01"
    name: "특이점 빌더스"
    desc: "AI 코딩 8주 부트캠프. <b>1기+2기 누적 70명+</b> 수료. DOE 프레임워크."
```

---

## § 12 — `contact` (object, required)

Colophon contact block.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `contact.mobile` | string | ✅ Required | Korean mobile preferred: `010-NNNN-NNNN`. Renders as-is | `"010-8216-8366"` |
| `contact.email` | string | ✅ Required | Valid email | `"sangrok@quantumjumpclub.com"` |
| `contact.website` | string | ✅ Required | Domain only (no `https://`) | `"qjc.app"` |
| `contact.issue_label` | string | optional | Override for the issue label. Default `Issue YY.MM.DD` from `issue_date` | `"Issue 26.05.01"` |

---

## § 13 — `social` (object, optional but recommended)

SNS handles. **Top-level placement** (not buried in contact) — verifiable proof signals belong above the fold of the colophon.

| Key | Type | Required | Validation | Example |
|-----|------|----------|------------|---------|
| `social.youtube` | string | optional | Domain + handle, no `https://` | `"youtube.com/@qjc_qjc"` |
| `social.instagram` | string | optional | Domain + handle | `"instagram.com/qjc.ai"` |
| `social.linkedin` | string | optional | Domain + handle | `"linkedin.com/in/sangrok-jung"` |
| `social.threads` | string | optional | Domain + handle | `"threads.com/@qjc.ai"` |

The renderer iterates only over keys present — omit any platform not used.

---

## Common mistakes

The mistakes below were observed during v6–v13 testing and are the most frequent rendering failures.

### 1. Forgetting `<b>...</b>` requires safe rendering

If a `desc` field contains `<b>` and the template author forgot to apply Jinja2's `|safe` filter (or autoescape was enabled without an exception), the output will render `<b>` literally on the PDF as text. The shipped templates apply `|safe` to `desc` and `lead`. When porting catalog styles, **preserve the `|safe` on `desc`, `lead`, and `quote.text`**.

### 2. Adding years to `background.steps`

A common impulse: `"2018-2020 엔코아 플레이데이터 ..."`. This breaks the design intent — the trajectory is dateless on purpose. Years invite credential-fraud interrogation; the proof of capability lives in `projects` and `clients`. Strip dates before rendering.

### 3. Lists with wrong cardinality

| Field | Required cardinality | Symptom if wrong |
|-------|----------------------|------------------|
| `metrics` | exactly 4 | grid breaks; renderer rejects |
| `clients` | 25–32 (target 32) | rows under-fill or overflow A4 |
| `products` | 5–9 (target 9) | grid gaps or page-2 overflow |
| `projects` | 5–10 | section overflows A4 if >10 |

The renderer warns when cardinality drifts. A founder with only 3 metrics is asked to either add a 4th proof axis or pick a different format.

### 4. Photo aspect ratio mismatch

Hero photo is rendered in a 4:5 frame (portrait). Submitting a 1:1 or 16:9 image causes object-fit cropping that often clips the subject's chin or top of head. Pre-crop to 4:5 before placing in `assets/photos/`.

### 5. Long `desc` overflowing one line

`projects[].desc` and `products[].desc` are designed for **one line**. Over ~110 chars they wrap and break the row rhythm. The renderer does not auto-truncate — verify the PDF before sending.

### 6. Path with `~` (tilde) home expansion

YAML does not expand `~`. Use absolute paths (`/Users/sangrok/...`) or skill-dir-relative paths (`assets/...`). `render.py` does not expand `~` either; this is by design (no shell-injection surface).

### 7. Hanja set to a Korean string

`name.hanja: "정상록"` (한글) breaks the design — the renderer applies a 한자-specific font (Noto Serif KR with Hanja subset) to that field. Submitting Korean characters renders them but in the wrong typographic weight. Either provide proper hanja (`"鄭常綠"`) or set to empty string `""`.

### 8. Trailing whitespace in YAML multiline

```yaml
lead: |
  이력 한 장이 아닌 ...   # ← trailing space breaks YAML in some parsers
```

PyYAML handles this, but if the file is hand-edited in an editor without trim-on-save, indentation drift causes silent parse errors. Use a YAML linter when adding many entries.

### 9. Missing `seal` / `seal_legal` for `swiss-seal` style

The `swiss-seal` style overlays a vermilion 朱印 stamp on the photo. If `seal` is missing, the style still renders but without the seal element — the design loses its distinguishing mark. Provide both `seal` (personal/한자) and `seal_legal` (法人印, corporate) when targeting Korean institutional contexts.
