# Section Rationale — Why Each of the 8 Sections Exists

> A founder portfolio is not assembled by adding sections — it is reduced to the sections that survive 13 cycles of testing. Across v2 → v13, every section that did not earn its place was removed. What remains here is what each section does, why it is positioned where it is, and which iteration revealed the lesson. The skill ships the structure as a constraint: the data file is portable, but the section list is not negotiable.

---

## 1. Top bar — brand mark + issue date

The strip across the very top of the page. Houses three elements: a brand line (typically `A founder portfolio.`), the founder's name in Latin script, and the issue date in `Issue YY.MM.DD` format. No content sits above it.

The top bar exists for two reasons. First, magazine masthead convention — a reader who has internalized The Economist or HBR cover layouts immediately reads "this is editorial, not promotional" from the top bar alone. The genre cue happens before any other parsing. Second, the issue date communicates that this is a **versioned document**: it was current as of the date printed, and the founder commits to re-issuing rather than letting the document drift. v2 omitted the date and reviewers flagged the document as "looks stale by default" — adding the issue date in v3 immediately fixed the perception. The `Est. {year}` line in the colophon (§ 9) is the company timeline; the top-bar issue date is the document timeline. They are not redundant.

---

## 2. Hero — photo + name (한자 병기) + role + lead

The largest section on the page. A 4:5 portrait sits in roughly 4 of the 12 columns; the remaining 8 columns hold the name (Latin display + 한글 + 한자 stack), the role line, and a 2–4 line lead paragraph.

The hero is the only section where the founder's face appears, and the only section where Korean hanja is rendered prominently. Both choices were validated through v3 → v5: photoless variants tested as "abstract" and were less remembered after a 24-hour delay, while versions without hanja read as less formal in B2B Korean institutional reviews. The lead paragraph is a flowing prose introduction, not a bullet list — v4 tried bullets here and reviewers reported "it reads like a LinkedIn About section, not a magazine," which was the exact failure mode the design was trying to avoid. Hero prose creates editorial tone; bullets create profile tone. The skill enforces prose by accepting `lead` as a multiline string with no list syntax.

---

## 3. Background trajectory — no dates, just the arrow chain

A single horizontal line (or wrapping flow) of 3–6 stops: institution + role per stop, joined by arrows. Examples: `백제예술대 미디어음악과 (작곡) → 엔코아 플레이데이터 → 경남대 빅데이터 연구원 → Founder, QJC`.

This is the most deliberate omission in the entire format. **Dated career sections invite credential-fraud interrogation; a trajectory line communicates path without forensic surface area.** The lesson came from v3 → v4: the v3 prototype had a dated CV-style "Experience" section (`2018–2020 엔코아 ...`), and reviewer feedback consistently centered on dates rather than work — "what were you doing in the gap year," "why is this overlap" — which converted the document from a proof-of-work piece into a CV-defense piece. Removing the dates in v4 redirected attention to the projects and clients sections (the actual proof). The trajectory line still communicates the founder's institutional path; it just refuses to make that path the document's center of gravity. Every shipped style preserves this rule.

---

## 4. Metrics — 4 quantified proof points

Four cells across the 12-col grid (3 cols each). Each cell shows one number plus one label: `1,000+ Total Students`, `29K+ YouTube · @qjc_qjc`, `26K+ Threads · @qjc.ai`, `30+ Clients of Record`.

Two questions: why exactly four, and why these specific four. **Four** is the cognitive sweet spot for at-a-glance metric strips — three reads as sparse and possibly cherry-picked, five-plus crosses into dashboard territory and breaks the editorial register. v6 tested 3-cell and 5-cell variants; reviewers consistently rated 4-cell as "professional," 3-cell as "thin," and 5-cell as "trying too hard." The grid math also favors four (12÷4 = 3 cols each, no remainder). **These specific axes** — students, audience reach, audience reach (second platform), client count — are the founder's universal proof axes for an education-and-consulting business: total people educated, public audience as a leading indicator of trust, and total enterprise relationships as a lagging indicator. v3 included a revenue figure (`매출 1.58억원`) which was removed in v4 after user feedback that **quantified income invites scrutiny without proportional credibility gain** — a number that says "we did this much business" reads as braggy unless paired with extensive context, which the format does not have room for. Audience and student counts carry the same authority signal at much lower social cost.

---

## 5. Pull quote — one positioning sentence

A centered, italicized, larger-than-body sentence with attribution beneath. One sentence — never two.

The pull quote exists because **a single positioning sentence is more memorable than a paragraph** of the same material. v5 had a positioning paragraph in this slot; reviewers could not recall any specific phrase from it 24 hours later. v6 compressed the paragraph into one sentence and reviewers could quote it back verbatim. The format borrows directly from magazine pull-quote convention, where the role of the pull quote is to give a reader who only scans the page one quotable line they can carry away. The Sangrok Jung default — "이력 한 장이 아닌 공개된 결과물로 검증되어 온 컨설턴트" — is also a positioning thesis: it directly counters the "credential fraud" vector and tells the reader where to look for proof (the projects/clients sections immediately below). The pull quote is positioned in the vertical center of the page: by the time the reader hits it, they have processed the hero and metrics, and the quote crystallizes what the rest of the page is arguing.

---

## 6. Selected Projects — 5–10 named engagements with status

Numbered rows. Each row carries a tag (`02 · Kakao · 5/14`), a project name (`하네스 세미나`), and a one-line description with a deliverable status flag: `제안서 v2 송부`, `1차 5/1 납품`, `완료`, `잔금 회수 완료 (1,045만원)`.

This format beat the alternatives across multiple v8–v11 cycles. The competing format was the vague rollup — `"AI 자동화 컨설팅을 다수 대기업에 제공"` (delivered AI consulting to enterprises). Reviewers consistently rated vague rollups as "could be anyone" and named-engagement-with-status as "this is real." **The named-engagement format is verifiable** — a reader can search "Kakao 하네스 세미나" and find evidence; the rollup gives them nothing to verify. The deliverable status (`v2 송부`, `납품 예정`, `완료`, `수금완료`) further sharpens the proof: it shows the founder operates with project-management precision rather than vague client lists. v9 tested whether removing the status was acceptable to keep the rows shorter — reviewers flagged the de-statused rows as "noticeably weaker." The status stays.

---

## 7. Clients of Record matrix — 32 entries, 4 cols × 8 rows

A flat grid: each cell shows a category tag (`Enterprise`, `University`, `EdTech`, `Publishing`, `Project`, etc.) and a `Client · Engagement` line. No prose, no grouping headers.

The flat matrix beat the categorized-text alternative because **scannability and density are the entire point of this section**. v7 tested a categorized version (`### Enterprise\n- 삼성전자\n- LG U+\n...\n### University\n- KNUA\n...`) and reviewers spent visibly longer reading it without absorbing more — the H3 headers added vertical real estate and broke the eye's ability to sweep the section. The flat 4×8 grid lets a reader cover all 32 entries in 5–8 seconds while still seeing the category distribution (because the `typ` tags are color-tinted in the cell). The matrix also forces the founder to commit to category labels rather than waffle. Reaching exactly 32 (and not "more than 25") was a v9 decision: 32 fills the grid completely with no awkward dangling row, and the round-square geometry signals "this is a complete picture" rather than "I picked some examples."

---

## 8. Self-Operated Products — 5–9 own product lines (founder signal)

A 3×3 grid of product cards. Each card: a number (`01`, `02`, ...), a product name, and a one-line description with a quantified anchor in bold (`<b>1기+2기 누적 70명+</b>`, `<b>활성 구독 173명</b>`, `<b>100+ 카탈로그</b>`).

This is the section a traditional CV does not have, and it is the section that most strongly signals founder rather than employee. **A traditional CV documents what someone has been hired to do; this section documents what someone has built and operates.** v8 introduced this section after observing that consultant-founder profiles routinely fail to differentiate from senior-consultant profiles — both list impressive clients, both list speaking engagements. The differentiator is not the client list (which both have) but the product list (which only the founder has). The numbered prefix (`01`, `02`, ...) signals that these are first-class business lines rather than side projects, and the quantified anchors (numbers in bold) anchor each product in concrete operational facts rather than aspirational language. v11 tested removing the numbers — the section read as a "miscellaneous side hustles" list. The numbers stay.

---

## 9. Colophon — contact + SNS handles + seal/signature

The bottom strip: mobile, email, website, issue label, and a row of SNS handles (YouTube, Instagram, LinkedIn, Threads). For Korean institutional styles, a vermilion 朱印 seal is overlaid in the lower right.

The colophon is the contact section, but it does work that a contact section in a traditional resume does not: **SNS handles deserve top-level placement now because they are verifiable proof.** A YouTube handle with 29K subscribers is a piece of evidence a recipient can independently verify in 5 seconds; a Threads handle with 26K followers is the same. v6 buried social handles in a small footer line; reviewers missed them. v9 promoted SNS to a dedicated colophon row at the foot of the page and reviewers explicitly cited "I checked his YouTube before replying" in follow-up interviews. In a market where any claim on a resume can be invented, a public-channel handle is one of the few pieces of evidence that resists fabrication — the followers are real, the upload history is timestamped, and the recipient can verify both without contacting the founder. The seal (where used) communicates the same kind of un-forgeable signal in the Korean institutional register: a registered 印鑑 carries legal weight. The colophon as a whole is structured around the principle that the document should not just claim but enable verification, and SNS placement at the foot of the page is the most public of those verification handles.
