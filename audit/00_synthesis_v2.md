# 종합 감사 보고서 v2 (회의적 재검토 반영)

**Date:** 2026-05-02
**Replaces:** `00_synthesis.md` (v1, 1차 검토 — 보존)
**Re-audit triggers:** Task 36 누락 / fal.ai 단일 출처 결론 / 메인 편향 검출

---

## TL;DR (v1 대비 변경분)

| v1 결론 | v2 수정 |
|---------|---------|
| ❌ "OpenAI BLOCKER, fal.ai 1순위, Imagen 2순위" | ⚠️ **Imagen 4 폐기 임박 (2026-06-24)** — 추천 자체 무효화. fal.ai 1순위 유지 단 데이터 조항 법률 검토 필요. OpenAI는 BLOCKER가 아닌 "회색지대 + 자기 사용 시 안전 측 회피". |
| ❌ MVP 변수 일관성 OK = 코드 OK | ⚠️ **#36 HIGH 2건**: Chrome macOS-only / `--style all` 첫 실패에 전체 중단. macOS 외 환경 즉시 크래시. |
| ❌ "보안 HIGH 2건은 배포 전 fix" | ⚠️ **HIGH 등급은 "배포 시" 기준이지 "자기 사용 시"는 MEDIUM**. 분기 표시 필요. |
| ❌ "5가지 사용자 결정사항" | ➕ **PIPA 제28조의8 동의 흐름** 6번째 결정 추가 (법적 강제). |

---

## 새로 발견된 의사결정 BLOCKER (v1 누락)

### B1. Google Imagen 4 — 7주 후 EOL ⚠️
- 공식 종료일: **2026-06-24** (imagen-4.0-{fast,generate,ultra}-001 모두)
- 35번 추천 "2순위 Imagen 4 Fast"는 7주 후 무효화
- 대체: Gemini 2.5 Flash Image — 단 Person Customization 공식 지원 여부 미검증

### B2. PIPA 제28조의8 국외 이전 동의 흐름 — 35번 완전 누락
- 얼굴 사진 = PIPA 민감정보 (생체정보), 별도 명시적 동의 필수
- 미국 fal.ai 서버 전송 시 사전 고지 5항목 + 거부권 동의 화면 필수
- 미준수 시 PIPC 행정 제재 대상 (2025-01 사례 존재)
- 플러그인 배포자 = 개인정보처리자 책임 일부 부담

### B3. #36 코드 HIGH 2건 — macOS 외 환경 즉시 크래시
| 파일:줄 | 이슈 | 임팩트 |
|---------|------|--------|
| `render.py:43` | Chrome 경로 macOS 하드코드 | Linux/CI 첫 실행 즉시 FileNotFoundError |
| `render.py:261` | `--style all` 첫 실패 시 `sys.exit(1)` | 5종 중 1개 실패 → 나머지 4개 미실행 |

수정 패턴:
```python
# Linux/macOS 통합
import shutil
chrome = next((p for p in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"),
    shutil.which("chromium-browser"),
    shutil.which("chromium"),
] if p), None)
if not chrome: raise FileNotFoundError("Chrome not found")

# --style all 부분 실패 허용
for style in styles:
    try: render_one(...)
    except Exception as e:
        failures.append((style, e))
        continue  # 다음 style 진행
```

---

## v2 추천 의사결정 6가지

| # | 결정 | v1 권장 | v2 수정 권장 | 시간 |
|---|------|---------|-------------|------|
| 1 | 이미지 공급자 | fal.ai | **fal.ai (1순위 유지) + Local Flux (Fallback)**. PIPA 안전 측이면 Local 우선. | — |
| 2 | 보안 fix | HIGH 2 즉시 | **macOS 외 즉시 fix**: 코드 HIGH 2 (Chrome path / --style all). 보안 HIGH는 "marketplace 배포 시점"으로 지연 가능. | 30분 |
| 3 | Phase A (GitHub) 시점 | 보안 fix 후 | **#36 HIGH 2건 + 보안 HIGH 2건 같이 fix 후** | 1.5h |
| 4 | 한자 텍스트 | Pillow overlay | 변경 없음 | 1h |
| 5 | PII 처리 | 자동삭제 + PIPA 28-8 | **PIPA 동의 흐름 정식 구현** (6번 항목으로 분리) | — |
| 6 | **PIPA 동의 흐름 구현** (신규) | — | **생체정보 별도 동의 + 국외 이전 5항목 고지 + 동의 로그 3년 보관** | 2h |

---

## 다음 사이클 추천 작업 순서 (v2, 약 5시간)

```
[30분] 코드 HIGH 2건 fix (render.py Chrome path + --style all 부분 실패 허용)
[30분] 코드 MEDIUM 5건 fix (name.split / seal_legal validation / venv 호환성 / --refresh / Chrome returncode)
[30분] 보안 HIGH 2건 fix (bleach + requirements.txt --require-hashes)
[2시간] generate_portrait.py (fal.ai Flux Kontext) + overlay_text.py (한자 Pillow)
[1.5시간] PIPA 동의 흐름:
  - privacy.md 작성 (이전받는 자 / 국가 / 목적 / 기간 / 거부권)
  - SKILL.md 첫 사용 시 동의 다이얼로그 (~/.claude/skills/founder-portfolio/.consent.json)
  - 동의 로그 3년 보관 + 삭제 요청 채널
[30분] README.md / .env.template / Phase A 배포
```

총 5시간 — 외부 1인 사용자에게 안전 배포 가능 상태.

---

## v2가 v1보다 신뢰할 만한 이유

| 영역 | v1 근거 | v2 근거 |
|------|---------|---------|
| OpenAI 정책 | researcher 단일 보고서 | researcher + codex MAJOR-1 + 정책 회색지대 인정 |
| fal.ai | researcher 단일 보고서 | researcher + Trust Center + ToS 직접 fetch |
| Imagen | researcher 단일 보고서 | researcher v2가 EOL 발견 (v1 미인지) |
| 코드 품질 | 메인 변수 일관성만 | code-reviewer 정식 감사 (audit/36) — HIGH 2 + MEDIUM 5 + LOW 4 |
| 종합 편향 | 메인 자체 종합 | codex 2nd opinion이 MAJOR 2 + MISSING 3 검출 |
| PIPA | 누락 | 별도 검증 — 의사결정 6번 항목으로 분리 |

---

## 참조

- `audit/00_synthesis.md` — v1 (보존, 잘못된 결론 포함)
- `audit/34_plugins_spec.md` — Plugin 사양 (변경 없음)
- `audit/35_image_pricing.md` — 가격 (Imagen 부분 무효, C로 보정)
- `audit/36_mvp_audit.md` — 코드 품질 (이번에 신규 생성)
- `audit/37_security.md` — 보안 (등급 분기 표시 권장)
- `audit/B_codex_2nd_opinion.md` — cross-model 2nd opinion (gpt-5)
- `audit/C_policy_xverify.md` — 정책 + PIPA 교차검증

---

## v3 사용자 결정 패치 (2026-05-06)

사용자 직접 지시: "GPT IMAGE2를 사용해야된다니까".

| v2 결정 | v3 적용 |
|---------|---------|
| 1순위 fal.ai Flux Kontext | **1순위 OpenAI gpt-image-2** |
| OpenAI = 회색지대 회피 (BLOCKER) | **사용자 책임 self-use 진행** (한자/한국어 정확도 강점) |
| privacy.md v1.0 (fal.ai 수신자) | **privacy.md v2.0 (OpenAI 수신자)** |
| `FAL_KEY` env var | **`OPENAI_API_KEY` env var** |
| fal.ai data URL CDN bypass | OpenAI default 30일 abuse monitoring (학습 미사용 2023-03+) |

### 근거

- 사용자 본인 사진 + 본인 OpenAI 키 + privacy.md v2.0 §7 self-use 책임 고지로 정책 회색지대를 명시 동의로 보완.
- OpenAI default policy(2023-03+): API 입력 데이터는 학습에 사용 안 함.
- gpt-image-2의 한자/한국어 텍스트 90%+ 정확도 (audit/35 §3 — 본 영역에서 fal/Imagen 모두 미달).
- PIPA 제22조의2(별도 동의) + 제28조의8(국외 이전 5항목) 요건은 consent.py 게이트로 충족.

### 변경 범위 (10 파일)

- 코어: `scripts/generate_portrait.py` (rewrite, openai SDK), `scripts/requirements.txt` (`openai==1.50.0` 추가), `scripts/forget_me.py` (수신자 변경)
- 설정: `.env.template` (`FAL_KEY` → `OPENAI_API_KEY`)
- 문서: `SKILL.md` (Phase 2 + PIPA 섹션), `README.md` (Quick start), `privacy.md` (v1.0 → v2.0 전체 갱신)
- 감사: `audit/35`, `audit/C`, `audit/00_synthesis_v2` (본 v3 패치)

### 유지

- PIPA 동의 게이트 (`consent.py` verify/grant/show/revoke)
- 약관 해시 invalidation (privacy.md v1.0 → v2.0 변경 시 기존 동의 자동 만료)
- `--consent-acknowledge` 자동화 플래그
- `--dry-run` 동의 게이트 면제 (no data leaves machine)
- `forget_me.py` 일괄 삭제 (입력·생성·동의기록)

### 잔존 리스크 (사용자 책임)

- OpenAI가 향후 self-use 케이스를 명시 차단 시 계정 제재 가능 → privacy.md v2.0 §7에 명시 고지
- 회피 옵션: `--presets editorial,monochrome` 등 변환 횟수 최소화 + 결과 PNG만 보존
- 입력 사진은 OpenAI 30일 보관 정책에 따라 자동 만료 추정

### Live test 다음 단계

```bash
# 1. openai 패키지 설치
bash ~/.claude/skills/founder-portfolio/scripts/bootstrap.sh

# 2. dry-run으로 프롬프트 + 비용 확인
.venv/bin/python scripts/generate_portrait.py \
  --source ~/me.jpg --dry-run

# 3. 실 호출 (5 PNG ~$0.20)
export OPENAI_API_KEY=sk-...
.venv/bin/python scripts/consent.py grant
.venv/bin/python scripts/generate_portrait.py \
  --source ~/me.jpg --out-dir ~/portraits
```
