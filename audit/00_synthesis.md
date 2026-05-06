# 종합 감사 보고서 (Synthesis)

**Date:** 2026-05-02
**Scope:** founder-portfolio MVP + Plugin 변환 + 이미지 생성 + 보안
**Verdict:** **MVP는 SHIP 가능, 단 BLOCKER 1건 + HIGH 2건 우선 해결 후 Phase A 배포**

---

## TL;DR (5줄)

1. 사용자가 가정한 **OpenAI gpt-image-2는 실제 인물 사진 정책 차단** — 공급자를 fal.ai Flux 1.1 Pro Kontext로 변경 필요 (BLOCKER)
2. **Plugin 변환은 지금 불필요** — GitHub repo + 1-line install (Phase A) 권장. Plugin은 Phase B로 보류
3. **보안 HIGH 2건**: pip 해시 미고정 (공급망), `autoescape=False` + `|safe` (XSS/file://)
4. **MVP 자체 품질은 양호**: 5종 템플릿 변수 일관성 OK (34/34 매핑), 5종 PDF 검증 통과
5. **사용자 결정 필요 5가지** (아래 표)

---

## 4개 Task 결과 요약

| # | 영역 | 핵심 결론 | 후속 |
|---|------|----------|------|
| 34 | Plugins 사양 | HYBRID — 지금은 Skill, 나중에 Plugin. 변환 비용 2-3h, 비가역성 없음 | Phase A: GitHub repo |
| 35 | 이미지 가격 | OpenAI 차단 / fal.ai Flux 1순위 ($0.04/장) / Imagen Fast 2순위 ($0.02/장) / Local Flux 폴백 | 공급자 변경 |
| 36 | MVP 품질 | 변수 일관성 OK, 렌더링 통과 (#37이 보안 이슈 cover) | 36 별도 문서 미생성, #37로 흡수 |
| 37 | 보안 | DISTRIBUTE_WITH_FIXES — HIGH 2 + MEDIUM 3 | 2-3시간 fix |

---

## BLOCKER · 사용자 가정 오류

> 사용자 진술: "사용자의 프로필 이미지도 넣고 그것을 기반으로 이미지도 생성해야한다 그렇기 때문에 이 플러그인을 사용하는 사람이 OpenAI api key도 사용자가 받아서 넣어야한다"

**문제:**
- OpenAI gpt-image-2는 2026-04 정책 강화로 **타인/본인 사진 업로드 후 초상 생성 차단**
- 정책 위반 시 계정 정지 리스크
- 사용자가 키를 발급받아도 작동하지 않음

**대안 (출처: Task 35 audit):**

| 순위 | 공급자 | $/장 | 10장 비용 | 본인 사진 OK | 한자 렌더 |
|------|--------|------|----------|-------------|----------|
| 1 | fal.ai Flux 1.1 Pro + Kontext | $0.04 | $0.40 | ✅ | ❌ (overlay 권장) |
| 2 | Google Imagen 4 Fast | $0.02 | $0.20 | ✅ (Person Customization) | ❌ |
| 3 | Local Flux.1 Dev | $0.00 | $0.00 | ✅ | ❌ |

**한자 명패 (예: `鄭常綠`)는 Pillow 후처리 overlay로 별도 합성** — 현재 `assets/seals/` 자산 활용 가능.

---

## HIGH 보안 이슈 (즉시 수정, ~30분)

### H1. `bootstrap.sh` pip 해시 미고정

```bash
# 현재 (취약)
"$VENV/bin/pip" install --quiet jinja2 pyyaml pillow

# 수정
"$VENV/bin/pip" install --require-hashes -r requirements.txt
```

`requirements.txt`에 정확한 버전 + SHA256 해시 고정. typosquat 공급망 공격 차단.

### H2. `render.py` `autoescape=False` + 전체 `|safe`

```python
# 현재 (취약)
env = Environment(loader=..., autoescape=False)

# 수정 — bleach로 화이트리스트 sanitization
import bleach
ALLOWED = ["b", "em", "i", "strong", "br"]
env.filters["safe_html"] = lambda v: bleach.clean(v, tags=ALLOWED, attributes={})
```

악성 `profile.yaml`이 `<script>` 또는 `<link href="file:///">` 주입 시 Chrome `--no-sandbox`가 로컬 파일 노출 가능.

---

## MEDIUM 이슈 (Phase A 배포 전 fix)

| # | 이슈 | fix |
|---|------|-----|
| M1 | `--no-sandbox` 플래그 | `--disable-file-access-from-files` 추가 또는 sandbox 활성화 |
| M2 | `.gitignore` 부재 | 루트에 `.venv/ .env *.pdf data/personal-*.yaml` 추가 |
| M3 | OpenAI 키 정책 미정 | `~/.claude/.env.secrets` 단일 원천 (QJC 규칙 준수). `profile.yaml`에 키 필드 절대 금지 |

---

## Phase A (GitHub repo 배포) — 권장 경로

**현재 상태로 Phase A 가능 (보안 fix 후)**:

```bash
# 사용자 측 설치 — 1-line
git clone https://github.com/qjc-app/founder-portfolio ~/.claude/skills/founder-portfolio
bash ~/.claude/skills/founder-portfolio/scripts/bootstrap.sh
# → 즉시 /founder-portfolio 사용 가능
```

**Plugin 변환 (Phase B)**은 사용자 50명+ 또는 marketplace 등록 의사가 생긴 후. 변환 비용 2-3h, 지금 미리 할 이유 없음 (출처: Task 34).

---

## 사용자 결정 필요 5가지

| # | 결정 | 옵션 | 영향 |
|---|------|------|------|
| **1. 이미지 공급자** | fal.ai / Imagen / Local | fal.ai 1순위 (정책 명확, 즉시 발급, $0.40/10장) | 공급자별로 generate_portrait.py 다름 |
| **2. 보안 HIGH 2건 즉시 fix** | YES / 묶어서 / 불필요 | 권장: YES (~30분) | Phase A 배포 전제조건 |
| **3. Phase A (GitHub) 시점** | 지금 / 보안 fix 후 / Phase B로 점프 | 권장: 보안 fix 후 (1-2일) | 다른 사람 사용 가능 시점 |
| **4. 한자 텍스트** | Pillow overlay / 무시 / GPT-image-2 별도 | 권장: Pillow overlay (가장 안정) | scripts/overlay_text.py 추가 |
| **5. PII 처리** | 사진 전송 후 자동 삭제 / privacy notice / 동의 chk | 권장: 자동 삭제 + SKILL.md에 PIPA 28-8 고지 | privacy.md 추가 |

---

## 다음 사이클 추천 작업 순서 (1.5일)

```
[30분] 보안 fix (HIGH 2 + MEDIUM 3)
  → bleach + requirements.txt + .gitignore + ~/.claude/.env.secrets 정책

[2시간] 이미지 생성 모듈
  → scripts/generate_portrait.py (fal.ai Flux 1.1 Pro Kontext)
  → scripts/overlay_text.py (Pillow 한자/이름 합성)
  → SKILL.md에 --generate-photos 플래그 추가

[30분] Phase A 배포 준비
  → README.md (1-line install 안내)
  → .env.template
  → privacy.md (PIPA 28-8 + GDPR equiv)

[1시간] GitHub repo 생성 + 푸시 + 첫 번째 외부 사용자 초대
```

---

## Risks user accepts even with all guardrails

1. fal.ai 약관 변경으로 정책이 OpenAI처럼 바뀔 가능성 (모니터링 필요)
2. 사용자가 본인 사진을 외부 API에 업로드 → 데이터 잔존 책임은 fal.ai
3. Plugin이 아닌 GitHub clone 방식이라 자동 업데이트 없음 (사용자가 직접 git pull)
4. Korean text overlay가 디자인을 미묘하게 깨뜨릴 수 있음 (베이스 디자인 후 overlay 합성 시)

---

## 참조

- `audit/34_plugins_spec.md` (super-research)
- `audit/35_image_pricing.md` (researcher)
- `audit/37_security.md` (security-reviewer)
- 메인 검증: 변수-스키마 일관성 5/5 템플릿 통과
