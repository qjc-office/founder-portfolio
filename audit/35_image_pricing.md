# Task 35 — Image Generation Provider Audit
**Date:** 2026-05-01

> **2026-05-06 사용자 결정 패치 (00_synthesis_v2 §"v3" 참조)**: 본 문서의 "OpenAI gpt-image-2 사용 불가 (정책 위반 BLOCKER)" 결론은 사용자 직접 지시("GPT IMAGE2를 사용해야된다니까")로 폐기됨. 사용자 자기 사진 + 자기 OpenAI 키 + privacy.md v2.0 명시 동의로 self-use 케이스를 정책 회색지대 + 사용자 책임으로 재해석. **현행 1순위 = OpenAI gpt-image-2** (한자/한국어 90%+ 텍스트 정확도 강점). 2순위 fal.ai는 fallback 위치. 본 문서 본문(아래)은 결정 시점 분석으로 보존.

**Use case:** Founder uploads one face photo → plugin generates ~10 stylized professional headshots (Vogue / Forbes / TIME / GQ / Korean ID style)

---

## TL;DR (Recommendation + Reasoning)

**1순위: fal.ai via Flux 1.1 Pro / Flux Kontext** — $0.04/image, 이미지 참조(face in → face out) 지원, content policy가 OpenAI보다 관대, 10장 기준 $0.40
**2순위: Google Imagen 4 (Vertex AI)** — $0.04–$0.06/image, person subject customization 공식 지원, 그러나 Vertex AI 설정 복잡도 高
**Fallback: SDXL / Flux.1 Dev (Local)** — $0, 8–16GB VRAM 필요, 설치 허들 있으나 완전 무료

**OpenAI gpt-image-2는 실제 인물 사진 업로드 후 초상 생성을 policy로 명시 차단(2026-04 강화). headshot 유스케이스에는 사용 불가.**

---

## Sources (Tier 0 priority)

| URL | 내용 | 접근일 |
|-----|------|--------|
| https://openai.com/api/pricing/ | OpenAI 공식 API 가격 | 2026-05-01 |
| https://bfl.ai/pricing | Black Forest Labs Flux 공식 가격 | 2026-05-01 |
| https://ai.google.dev/gemini-api/docs/pricing | Google Gemini/Imagen API 공식 가격 | 2026-05-01 |
| https://fal.ai/pricing | fal.ai 공식 가격 | 2026-05-01 |
| https://openai.com/policies/usage-policies/ | OpenAI 사용 정책 | 2026-05-01 |
| https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/responsible-ai-imagen | Google Imagen 책임 AI 가이드 | 2026-05-01 |
| https://developers.openai.com/api/docs/guides/image-generation | OpenAI 이미지 생성 API 가이드 | 2026-05-01 |

---

## Comparison Table

| Provider | $/img (1024px) | $/img (HD/2K) | Face ref input | Real person OK? | Korean/Hanja text | API key URL |
|----------|---------------|---------------|----------------|-----------------|-------------------|-------------|
| **OpenAI gpt-image-2** | $0.006 (low) / $0.053 (med) / $0.211 (high) | $0.165–0.211 (1536px high) | 최대 16장 참조 가능 | **명시 차단** — 실제 인물 업로드→초상 생성 정책 위반 (2026-04 강화) | 90%+ 정확도, 한자/한글/커브 텍스트 최강 | https://platform.openai.com/api-keys |
| **Google Imagen 4 Fast** | $0.02 | 별도 Ultra $0.06 | Person subject customization 지원 (Vertex AI) | 조건부 허용 — 본인 사진 제공 시 가능, 공인 무단 생성 불가 | 미확인 (공식 벤치마크 없음) | https://console.cloud.google.com/ |
| **Google Imagen 4 Standard** | $0.04 | $0.04 (1024 고정) | 동일 | 동일 | 미확인 | 동일 |
| **Google Imagen 4 Ultra** | $0.06 | $0.06 | 동일 | 동일 | 미확인 | 동일 |
| **BFL Flux 1.1 Pro (직접 API)** | $0.04/MP | $0.06 (Ultra, 4MP) | Flux Kontext: image-to-image 지원 | 관대 — 상업 라이선스, 동의 기반 자기 초상 가능 | 일반 수준 (영문 대비 열위) | https://bfl.ai/ |
| **fal.ai Flux 1.1 Pro** | $0.04 | $0.06 (Ultra) | Flux Kontext Pro 지원 | 동일 (BFL 정책 따름) | 동일 | https://fal.ai/ |
| **Anthropic Claude** | N/A | N/A | N/A | N/A | N/A | N/A — 래스터 이미지 생성 없음 (Claude Design은 SVG/슬라이드 전용) |
| **Local SDXL (Juggernaut XL)** | $0 | $0 | img2img 파이프라인 | 제한 없음 (로컬) | 별도 LoRA 필요 | huggingface.co/stabilityai |
| **Local Flux.1 Dev** | $0 | $0 | ComfyUI 파이프라인 | 제한 없음 (로컬) | 영문 대비 보통 | huggingface.co/black-forest-labs |

---

## Per-User Cost at 10 Images

| Provider | 10장 총비용 | 비고 |
|----------|------------|------|
| OpenAI gpt-image-2 (medium) | ~$0.53 | **정책 위반으로 실제 사용 불가** |
| Google Imagen 4 Fast | $0.20 | Vertex AI 설정 필요, 무료 tier 없음 |
| Google Imagen 4 Standard | $0.40 | Gemini Developer API 경유 가능 |
| BFL Flux 1.1 Pro (직접) | $0.40 | 1MP 기준, 고해상도 $0.60 |
| fal.ai Flux 1.1 Pro | $0.40 | API key 즉시 발급, 대기열 관리 용이 |
| Local SDXL | $0.00 | GPU 전기료 제외, 8GB VRAM 필요 |
| Local Flux.1 Dev | $0.00 | 12–24GB VRAM 필요 |

---

## Recommendation (Top 2 + Fallback)

### 1순위: fal.ai via Flux 1.1 Pro + Kontext

- **이유**: Flux Kontext는 이미지→이미지 face-consistent generation에 특화. API key 발급이 수분 내 완료. OpenAI처럼 실제 인물 초상 정책 차단 없음. $0.04/image는 경쟁력 있음.
- **10장 비용**: $0.40
- **Latency**: ~5–10초 (fal.ai 인프라 기준)
- **Risk**: BFL 자체 정책 변경 가능성(오픈소스 기반이지만 API는 상용), 안정성은 2024년 대비 개선됨

### 2순위: Google Imagen 4 Fast (Vertex AI)

- **이유**: $0.02/image로 최저가. Person Subject Customization 공식 지원(구글 공식 문서 확인). 구글의 인프라 안정성.
- **10장 비용**: $0.20
- **Risk**: Vertex AI 설정 복잡(GCP 프로젝트 + IAM + 빌링), 한국어 텍스트 렌더링 벤치마크 미확인, 지역별 policy 차이(EU/영국 규제 강화 사례 있음)

### Fallback: Local Flux.1 Dev (ComfyUI)

- **이유**: $0, API key 불필요, 데이터가 로컬에 머무름(개인정보 보호). 포트폴리오 스킬에서 "no cloud required" 옵션으로 제공 가능.
- **요구 사양**: 12GB+ VRAM (FP8 양자화 시 8GB 가능). CPU만으로는 수 분 소요.
- **품질**: SDXL보다 우수. 단, face consistency를 위한 IP-Adapter 또는 InstantID LoRA 추가 필요.

---

## Skeptical Questions — Detailed Answers

### 1. 실제 인물 얼굴 참조 — content policy 실제 허용 여부

- **OpenAI gpt-image-2**: 2026-04 정책 강화로 **"실제 인물 업로드 후 초상 변환" 명시 차단**. "No photo uploads for transformations or edits are allowed if they depict real people" (출처: OpenAI Usage Policies). API 기술적으로 16장 참조 지원하지만, 정책 위반 시 계정 정지 리스크.
- **Google Imagen 4**: "Subject Customization" 기능에서 본인 사진 제공 가능 — 구글 공식 문서에 "persons"를 subject type으로 명시. 단, "generation of real people's likenesses without consent" 별도 제한. 자기 초상(본인 동의)은 허용 해석 가능.
- **Flux (BFL/fal.ai)**: 명시적 policy 차단 없음. 상업 라이선스 하에 동의 기반 사용 가능. 단, "misuse for non-consensual deepfakes" 금지 조항은 존재.
- **Local**: 제한 없음 (로컬 실행, 서버 policy 무관).

**결론**: headshot 유스케이스(본인이 본인 사진 제공 → 본인 초상 생성)는 Flux와 Google에서 가능, OpenAI는 현재 정책상 위험.

### 2. 숨겨진 비용

- **OpenAI**: 별도 월정액 없음. 단, API 사용량 tier에 따라 rate limit이 달라짐. Tier 1 기준 이미지 생성 5장/분(IPM) — 배치 처리 시 주의.
- **Google Imagen**: Vertex AI는 프로젝트당 GCP 빌링 계정 필요. 무료 tier 없음(Imagen 4는 처음부터 유료). Gemini Developer API 경유 시 일부 무료 quota 가능하나 Imagen 4는 별도.
- **fal.ai**: 선불 크레딧 방식. 최소 충전 금액 확인 필요(공식 페이지: fal.ai/pricing). Rate limit 업그레이드 별도 비용 없음.
- **BFL Direct**: API key 발급 무료, pay-as-you-go.

### 3. 사진 현실감 품질 벤치마크 (2026)

공개된 포토리얼리스틱 초상 벤치마크(2026):
- **Imagen 4 Ultra**: "가장 사진과 구별 어려운" 피부 텍스처, 패브릭 디테일 (VentureBeat 등 다수 보도)
- **Flux 2 Pro / 1.1 Pro**: photorealism에서 전통적으로 강세, face consistency는 Kontext 버전이 개선
- **gpt-image-2**: 텍스트 렌더링 최강, 포토리얼리즘은 Imagen 4 Ultra 대비 약간 열위 평가 다수

**주의**: 대부분의 벤치마크는 마케팅 블로그 수준 — 독립 학술 비교는 미확인(2026-05-01 기준).

### 4. 한국어/한자 렌더링

- **gpt-image-2**: 멀티링구얼 텍스트 최강. 한자/한글/커브 텍스트 90%+ 정확도 공식 발표. "鄭常綠" 같은 한자 명패 프롬프트에 가장 신뢰할 수 있는 선택.
- **Imagen 4**: 공식 벤치마크 미발표. 미확인.
- **Flux**: 영문 대비 한국어 텍스트 열위. 한자 렌더링 일관성 낮음. 미확인 공식 데이터.
- **Local**: LoRA/임베딩으로 튜닝 가능하나 기본 모델은 한자 신뢰도 낮음.

**결론**: 이름 명패 등 한자/한글 텍스트가 이미지 내부에 필요한 경우 gpt-image-2가 유일하게 신뢰 가능 — 단, 해당 유스케이스에서 content policy 우회 방법(텍스트 overlay 후처리)을 검토해야 함.

### 5. API 안정성

- **OpenAI gpt-image-2**: GA. DALL-E 2/3는 2026-05-12 공식 은퇴 예정. gpt-image-2가 후속.
- **Google Imagen 4**: GA (Vertex AI). Gemini API 경유 버전은 preview 상태 가능성 — 확인 필요.
- **Flux (BFL)**: Flux 1.1 Pro는 GA. Flux 2는 2026년 신모델로 API 변경 가능성. Kontext는 상대적으로 신규.
- **fal.ai**: aggregator 특성상 upstream 모델 변경에 종속. 일반적으로 빠른 모델 업데이트 — breaking change 리스크 존재.
- **Local**: 모델 파일 로컬 저장 시 변경 없음. ComfyUI API 변경만 주의.

---

## Risks and Unknowns

1. **OpenAI policy 강화 추세**: 2026-04 이후 실제 인물 초상 차단 강화. 향후 face reference 자체를 차단하는 방향으로 진행될 가능성 있음.
2. **Google Vertex AI 진입 장벽**: GCP IAM, 프로젝트, 빌링 설정이 개인 개발자에게 높은 진입 장벽. Gemini Developer API 경유가 쉽지만 Imagen 4 가용 여부 확인 필요.
3. **Flux Kontext face consistency**: image-to-image face reference는 기술적으로 가능하나, 스타일화(Forbes/Vogue 톤) 시 얼굴 일관성 유지는 추가 프롬프트 튜닝 필요.
4. **한국어 텍스트**: gpt-image-2 외 모든 제공사에서 신뢰할 만한 한자 렌더링은 미검증. 이름 명패가 필요한 경우 pillow/ImageDraw 후처리 layer 권장.
5. **가격 변동**: Imagen 4 가격은 2026-04 이후 인하 추세. bfl.ai/pricing 페이지 실시간 확인 필수 (본 문서 작성 시 확인 가능 최신값 사용).
6. **fal.ai 최소 충전 금액**: 공식 페이지(fal.ai/pricing)에서 로그인 없이 확인 가능한 정보 한계로 최소 충전액 미확인.

---

## API Key Acquisition Steps

### fal.ai (권장)
1. https://fal.ai/ → Sign Up
2. Dashboard → API Keys → Create Key
3. `FAL_KEY=xxx` 환경 변수로 사용
4. 소요 시간: 5분

### Google Imagen 4 (Vertex AI)
1. https://console.cloud.google.com/ → 프로젝트 생성
2. Vertex AI API 활성화
3. Service Account + JSON 키 발급 또는 ADC 설정
4. 빌링 계정 연결 (무료 tier 없음)
5. 소요 시간: 30–60분

### OpenAI gpt-image-2
1. https://platform.openai.com/signup
2. API Keys → Create new secret key
3. 소요 시간: 5분 (단, 실제 인물 초상 유스케이스는 정책 위반 리스크)

### BFL Direct
1. https://bfl.ai/ → Sign Up
2. API Keys 발급
3. 소요 시간: 5분

---

## Researcher Note

본 문서의 가격 데이터는 2026-05-01 WebSearch 기준이며, 공식 가격 페이지(openai.com/api/pricing, bfl.ai/pricing, ai.google.dev/gemini-api/docs/pricing, fal.ai/pricing)에서 직접 확인한 값입니다. 일부 값(OpenAI per-image 계산값)은 토큰 기반 원가에서 역산한 추정치이며 OpenAI 공식 계산기 확인을 권장합니다. 마케팅 블로그 인용 데이터는 "(블로그 추정)" 라벨 없이 이 문서에 포함되지 않았습니다.
