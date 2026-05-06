# Cross-verification: 이미지 공급자 정책 + 한국 PIPA 흐름

**검증자:** researcher (독립) · **검증일:** 2026-05-02
**대상:** `audit/35_image_pricing.md`
**(주: 본 파일은 researcher가 권한 부족으로 저장하지 못한 출력을 메인이 보존한 사본)**

> **2026-05-06 사용자 결정 패치 (00_synthesis_v2 §"v3" 참조)**: 본 문서의 "OpenAI gpt-image-2 정책 위반 BLOCKER" 결론은 사용자가 명시 거부. self-use 케이스(사용자 본인 사진 + 본인 키 + 본인이 정보주체)는 OpenAI 정책 회색지대로, privacy.md v2.0의 명시 동의 흐름이 PIPA 제22조의2(별도 동의) + 제28조의8(국외 이전 5항목) 요건을 충족함. 1순위 fal.ai 추천 → **1순위 OpenAI gpt-image-2 + Fallback fal.ai/Local Flux**로 재정렬. PIPA 동의 게이트(consent.py) + 약관 해시 invalidation은 변경 없이 유지. 본 문서 본문(아래)은 결정 시점 분석으로 보존.

---

## TL;DR — audit/35_image_pricing.md와의 일치·불일치

1. **OpenAI 차단 — 확인됨.** gpt-image-2 실제 인물 정책 차단은 복수 Tier 0 검증. 단 "본인 동의 자기 업로드" 예외 여부는 공식 문서에 분리 기술 없음 — 회색지대 잔존.
2. **Google Imagen 4 2순위 — 즉시 수정 필요.** Imagen 3·4 전 라인 **2026-06-24 공식 Shutdown 예정**. 7주 내 무효화. Gemini 2.5 Flash Image가 공식 대체 경로 (Person Customization 재검증 필요).
3. **PIPA 동의 흐름 — 35번에서 완전 누락.** 얼굴 사진은 PIPA 민감정보(생체정보), 별도 동의 + 국외 이전 5항목 고지 필수. 공급자 선정보다 법적 위험 우선순위가 더 높다.

---

## Sources (Tier 0 우선)

| URL | 내용 | 신뢰도 |
|-----|------|--------|
| https://openai.com/policies/usage-policies/ | OpenAI 공식 사용 정책 | Tier 0 |
| https://deploymentsafety.openai.com/chatgpt-images-2-0 | ChatGPT Images 2.0 System Card | Tier 0 |
| https://fal.ai/legal/terms-of-service | fal.ai 공식 ToS | Tier 0 |
| https://fal.ai/legal/privacy-policy | fal.ai 공식 개인정보처리방침 | Tier 0 |
| https://fal.ai/docs/documentation/model-apis/media-expiration | fal.ai 데이터 보존 공식 문서 | Tier 0 |
| https://trust.fal.ai/ | fal.ai Trust Center | Tier 0 |
| https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/subject-customization | Google Person Customization 공식 | Tier 0 |
| https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate | Imagen 4 모델 문서 | Tier 0 |
| https://casenote.kr/법령/개인정보_보호법/제28조의8 | PIPA 제28조의8 법령 전문 | Tier 0 |

---

## OpenAI gpt-image-2 — "본인 동의 자기 사용" 회색지대

- 공식 정책: 동의 없이 실제 인물 photorealistic 생성 명시 금지
- 안전 분류기: 입력 + 출력 동시 검사 다중 레이어
- **회색지대**: 정책 문언이 (a) 타인 무단과 (b) 본인 동의 자기 업로드를 분리 기술하지 않음
- Aragon AI / ProfilePicture.AI가 OpenAI 경유인지 불명 — 자체 모델일 가능성 높음

**결론**: "사용 불가" 판단은 안전 측 기준에서 타당. 본인 동의로 시도하려면 OpenAI 지원팀 사전 확인 필수 (계정 정지 리스크 부담).

---

## fal.ai — 1순위 가능, 단 데이터 조항 주의

**회사 안정성 (Tier 1 복수 확인)**:
- Series C $125M (2025-07) → Series D $140M (2025-12, $4.5B valuation) → 2026-03 추가 라운드 ($8B 논의)
- 창립 2021 SF 본사. 단 등기 일부 **Anguilla** (포괄 개인정보보호법 없음)
- 단기 폐업 위험 낮음

**데이터 보존 (Tier 0)**:
- CDN 기본 7일, `X-Fal-Object-Lifecycle-Preference` 헤더로 조정
- `return_as_data_uri: true` 옵션 → CDN 저장 우회 (PIPA 준수 설계 시 필수)

**ToS 주의 (Tier 0)**:
- "Usage Data" fal 소유 + 모델 개선·분석 목적 제3자 공유 가능
- Usage Data가 업로드된 얼굴 사진 자체를 포함하는지 문언 모호 → **법률 검토 필요**

---

## Google Imagen 4 — 2026-06-24 EOL ⚠️

**Shutdown (Tier 0 확인)**:
- `imagen-4.0-generate-001`, `imagen-4.0-ultra-generate-001`, `imagen-4.0-fast-generate-001` 모두 2026-06-24 종료
- Imagen 3도 동일 날짜
- 공식 마이그레이션: `gemini-2.5-flash-image` ("Nano Banana")

**Person Customization**:
- Imagen 4: `subject_type: person` 지원 확인
- Gemini 2.5 Flash Image: face reference 공식 지원 여부 불명 — 재검증 필요

**리전**: us-central1 / europe-west2 / asia-northeast3 (도쿄). 서울 직접 리전 없음.

---

## PIPA + GDPR 사진 전송 동의 흐름

### 법적 지위
- **얼굴 사진은 PIPA 제23조 민감정보 (생체정보)** — 별도 명시적 동의 필수
- 2025-01 PIPC, 국외 이전 고지 미비 기업 행정 제재 부과 사례 (Tier 1)

### PIPA 제28조의8 국외 이전 — 사전 고지 5항목
fal.ai 미국 서버 전송 시:
1. **이전받는 자**: fal (Features & Labels Inc.), support@fal.ai
2. **이전 국가**: 미국
3. **이전 목적**: AI 초상 생성
4. **보유·이용 기간**: 처리 후 최대 7일 (CDN)
5. **거부 권리 + 불이익**: 거부 시 서비스 이용 불가

### 구체적 동의 화면 (필수)
```
[얼굴 사진 업로드 직전 — 일반 약관과 별도]

□ [필수] 생체정보(얼굴 사진) 처리 동의
   "AI 초상 생성 목적으로만 사용. 7일 이내 fal.ai 서버 삭제."

□ [필수] 개인정보 국외 이전 동의
   이전받는 자: fal (Features & Labels Inc.)
   이전 국가: 미국
   이전 목적: AI 이미지 생성
   보유 기간: 처리 후 최대 7일
   거부 시 서비스 이용 불가
```

### 감사 로그 최소 요건
- 동의 일시 (ISO 8601)
- 동의 버전 (약관 개정 추적)
- 사용자 식별자 / 세션 ID
- **3년 이상 보관**

### 플러그인 개발자 책임
PIPA "개인정보처리자"는 처리 흐름을 설계·배포하는 자 포함. 사용자 자신의 키 + 자체 머신 호출이라도 개발자가 오케스트레이션 로직을 설계·배포하면 책임 일부 잔존.
- 개인정보처리방침 게시
- 위 동의 흐름 구현
- 국외 이전 고지
- 데이터 삭제 요청 채널 (PIPA 제36조)

---

## Revised provider ranking

| 순위 | 공급자 | $/장 | 정책 | 2026-06 생존 | PIPA 국외이전 |
|------|--------|------|------|--------------|---------------|
| **1** | fal.ai Flux 1.1 Pro / Kontext | $0.04 | 차단 없음 | 생존 | 미국, 동의 필요 |
| **2** | Gemini 2.5 Flash Image | 미확인 | Person Custom 재검증 | 생존 | 미국·EU, 동의 필요 |
| ~~폐기~~ | ~~Imagen 4 Fast~~ | $0.02 | 지원 | **2026-06-24 종료** | — |
| ~~폐기~~ | ~~OpenAI gpt-image-2~~ | $0.053 | 실제 인물 차단 | 생존 | 정책 위반 |
| **Fallback** | Local Flux.1 Dev | $0 | 제한 없음 | N/A | 이전 없음 (PIPA 최안전) |

---

## 즉시 조치 3건

1. `35_image_pricing.md` "2순위 = Imagen 4 Fast" → "2순위 = Gemini 2.5 Flash Image (Person Customization 재검증 후 확정)"
2. 플러그인에 PIPA 동의 흐름 (생체정보 별도 동의 + 국외 이전 5항목 고지) 추가
3. fal.ai Usage Data 조항 입력 이미지 포함 여부 — 공식 문의 또는 법률 검토
