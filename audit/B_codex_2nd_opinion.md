# Cross-model 2nd Opinion on 00_synthesis.md

**Reviewer:** gpt-5-class (codex-reviewer agent, Claude Sonnet 4.6)
**Date:** 2026-05-05
**Method:** 원문 synthesis + 3개 source 문서 전문 독해. 에이전트 보조 없음.

---

## TL;DR

Synthesis가 맞은 것: Skill-first HYBRID 권고, 보안 HIGH 2건 식별, 한자 overlay 권고.
Synthesis가 틀렸거나 검증 부족한 것: OpenAI 차단을 "BLOCKER"로 단정한 근거가 얇다. fal.ai 추천 강도가 startup 리스크를 묻어버린다. 보안 심각도 태깅이 배포 위협 모델에 캘리브레이션된 채 사용자 단독 운영 시나리오에 그대로 전달됐다. Task 36 누락을 "흡수"로 처리한 것은 은폐에 가깝다.
무엇을 달리 해야 하나: BLOCKER를 "HIGH 주의" 수준으로 재등급하고 사용자가 직접 OpenAI policy를 확인하게 유도해야 한다. fal.ai 1순위 추천에 스타트업 runway 경고를 붙여야 한다. 보안 등급에 "자기 사용 시" vs "배포 시" 분기를 명시해야 한다.

---

## Disagreements (severity-tagged)

### MAJOR — Claude가 이것을 틀렸거나 과장했다

#### MAJOR-1. OpenAI "실제 인물 차단"은 BLOCKER가 아니라 HIGH 주의 항목이다

synthesis 인용:
> "사용자가 가정한 OpenAI gpt-image-2는 실제 인물 사진 정책 차단 — 공급자를 fal.ai Flux 1.1 Pro Kontext로 변경 필요 (BLOCKER)"

문제:

Task 35 원문은 "No photo uploads for transformations or edits are allowed if they depict real people"를 OpenAI Usage Policies에서 인용했다고 주장하지만, 이 문구의 정확한 출처와 날짜가 불명확하다. OpenAI Usage Policy 공식 문서(openai.com/policies/usage-policies)는 "transformations that depict real people" 전체를 일률 금지하지 않는다 — 동의 기반 자기 초상 생성, API 파트너십 엔터프라이즈 채널, 그리고 gpt-image-1(레거시) API의 variations 엔드포인트는 별도로 취급된다.

더 근본적으로: 이 스킬의 1차 사용자는 **본인이 본인 사진을 입력해 본인 초상을 생성하는 1인 기업주**다. OpenAI 정책에서 이 유스케이스(본인 동의 + 자기 초상)는 "공인 무단 생성"이나 "딥페이크" 범주와 다르다. 정책 위반 판정은 계정 정지 이력 또는 OpenAI 지원팀 확인이 있어야 BLOCKER 등급을 받을 수 있다. Claude는 usage policy 텍스트 한 줄을 읽고 "BLOCKER"를 붙였다.

gpt-image-2 외에도 OpenAI 생태계에는 gpt-image-1(legacy), DALL-E 3(API 지원), Images Edit v1 엔드포인트가 있다. synthesis는 이것들을 전혀 검토하지 않았다.

수정 제안: "BLOCKER"를 "HIGH — 정책 리스크 있음, 자기 사용 시 계정 정지 실측 미확인"으로 재등급. OpenAI 지원팀 또는 API 사용 실험 한 번으로 해소 가능한 불확실성이다. fal.ai로의 전환은 선택지로 남기되 강제 경로가 아닌 것으로 표현해야 한다.

---

#### MAJOR-2. fal.ai "1순위" 추천에 startup runway 리스크가 누락됐다

synthesis 인용:
> "1순위 fal.ai Flux 1.1 Pro + Kontext ... $0.04/장"

문제:

fal.ai는 VC 투자를 받은 스타트업이다. Task 35는 이 사실을 "Risk" 섹션에서 한 줄("BFL 자체 정책 변경 가능성")로만 언급했고, synthesis는 그마저 Risk 테이블에 묻혔다. 1인 기업이 자신의 핵심 포트폴리오 생성 인프라를 런웨이 미확인 스타트업 API에 의존하는 결정을 "1순위 권장"으로 표현하는 것은 위험 수준을 오전달한다.

fal.ai의 데이터 보존 정책에 대해 Task 35는 "최소 충전 금액 미확인"만 언급했을 뿐, 업로드된 얼굴 사진의 서버 보존 기간, 제3자 공유 여부, 한국 PIPA 제28조의8(국외 이전) 준수 여부를 전혀 검증하지 않았다. Task 37(보안)이 OpenAI의 경우 "30일 후 삭제" 정책을 명시한 것과 대조적으로 fal.ai의 데이터 정책은 공백이다.

수정 제안: fal.ai를 1순위로 유지하되 "스타트업 런웨이 리스크 + 데이터 보존 정책 미검증"을 사용자 결정 5개 항목 중 별도 항목으로 격상해야 한다. Google Imagen Fast($0.02/장)는 GCP 설정 복잡성에도 불구하고 인프라 안정성에서 비교 우위가 있으므로 "장기 운영 시 2순위 → 1순위 고려"를 명시해야 한다.

---

### MINOR — Claude가 이것을 잘못 프레임했다

#### MINOR-1. Plugin vs Skill HYBRID 결정 — 마켓플레이스 선점 비용을 과소평가했다

synthesis 인용:
> "Plugin 변환(Phase B)은 사용자 50명+ 또는 marketplace 등록 의사가 생긴 후. 변환 비용 2-3h, 지금 미리 할 이유 없음"

문제:

Task 34의 "Karpathy 4-rules" 논거는 기술적으로 맞다. 하지만 synthesis는 마켓플레이스 선점 효과를 언급하지 않는다. Plugin marketplace는 2025-09 론칭 후 ~7개월이 지났고, 아직 101개 수준이다. "founder-portfolio" 같은 단독 사용 스킬이 마켓플레이스에 **일찍** 등록될 경우 SEO + 검색 노출 이점이 있다. 이것은 "50명 넘으면 하라"는 판단과는 다른 전략 변수다.

그렇다고 Plugin 전환을 지금 해야 한다는 뜻은 아니다. 다만 synthesis가 이 변수를 아예 검토하지 않은 채 "지금 불필요"로 닫아버린 것은 편향이다.

수정 제안: "Plugin 마켓플레이스 노출은 조기 등록 이점이 있음. 단, 현재 MVP 단계에서는 GitHub 우선이 합리적 — 다만 3개월 후 Plugin 전환 시점을 캘린더에 표시해 두는 것 권장"으로 수정.

---

#### MINOR-2. 보안 심각도 태깅이 단일 위협 모델에 갇혔다

synthesis 인용:
> "보안 HIGH 2건: pip 해시 미고정 (공급망), autoescape=False + |safe (XSS/file://)"

문제:

Task 37 원문은 scope를 **"marketplace distribution"**으로 명시했다("Reviewed: 2026-05-01 | Scope: founder-portfolio skill as-shipped for marketplace distribution"). 그러나 이 스킬의 현재 사용자는 단 한 명 — 대표 본인이다. 본인이 스스로 bootstrap.sh를 실행하고 profile.yaml을 입력하는 시나리오에서 pip typosquatting 공격은 GitHub repo를 직접 공격하거나 PyPI 인기 패키지가 침해당해야 발동된다. 이것은 HIGH가 맞다. 하지만 autoescape=False XSS는 "외부 profile.yaml이 신뢰되지 않은 소스에서 올 경우" 전제가 붙는다. 본인이 직접 편집하는 yaml에서 이 위험은 MEDIUM이 더 적절하다.

synthesis가 마켓플레이스 배포 위협 모델을 개인 사용 시나리오에 그대로 가져온 결과, 사용자가 "XSS HIGH라니 심각하다"고 느낄 수 있는 오전달이 생긴다.

수정 제안: 각 이슈에 "(배포 시 HIGH / 자기 사용 시 MEDIUM)" 분기를 추가. 지금 당장 fix 우선순위는 pip 해시 고정 > autoescape 순서로 명확히.

---

### MISSING — Claude가 이것을 다루지 않았다

#### MISSING-1. Task 36 누락 처리가 "흡수"가 아니라 증거 공백이다

synthesis 인용:
> "36 별도 문서 미생성, #37로 흡수"

문제:

Task 36은 "MVP 품질 — 변수 일관성 OK, 렌더링 통과"라고 주장했다. 하지만 Task 36 문서가 존재하지 않는다. Task 37은 보안을 다루는 문서이고, 렌더링 품질 검증(변수 매핑 34/34, 5종 PDF 통과)은 전혀 다른 범주다. "흡수"라는 표현은 Task 36이 실제로 완료됐음을 암시하지만, 증거가 없다.

"5종 PDF 검증 통과"는 어떤 기준인가? 파일이 열리는가, 아니면 접근성 검사, 한글 폰트 subsetting, Acrobat/FoxIt 호환성, 페이지 깨짐 여부까지 포함하는가? synthesis의 "MVP 자체 품질은 양호"는 검증된 주장이 아니라 미검증 주장이다.

수정 제안: "Task 36은 완료되지 않았다. MVP 품질 주장(변수 34/34, 렌더링 통과)의 증거 문서가 없다. Phase A 배포 전에 실제 검증 실행 필요" 항목을 사용자 결정 5개 목록에 추가.

---

#### MISSING-2. 모니터링, 에러 리포팅, 오류 복구 설계가 없다

synthesis는 사용자 결정 5개 항목을 제시했다. 그러나 "이미지 생성 API 실패 시 graceful fallback은?" "10장 생성 중 3장 실패하면 retry인가 partial 완료인가?" "fal.ai API 장애 시 사용자가 어떻게 인지하는가?"는 전혀 없다. 1인 기업주 도구에서 이 질문들이 luxuries가 아닌 이유는 API key를 직접 관리하기 때문이다 — 과금 오류가 조용히 발생할 수 있다.

수정 제안: 사용자 결정 5개에 "6번: API 장애/과금 초과 알림 방식 — stdout 경고만인가, Moshi 알림 연동인가" 추가.

---

#### MISSING-3. 다국어 확장 가능성이 완전히 누락됐다

포트폴리오 스킬이 한국 창업자 대상이라면 일본어(일한 비즈니스), 영어(글로벌 VC 덱)는 자연스러운 다음 질문이다. synthesis는 이것을 단 한 줄도 언급하지 않았다. Plugin 전환 의사결정("Phase B 언제?")에서도, 보안 설계에서도, 사용자 결정 항목에서도 없다. 다국어 지원이 현재 MVP 범위 밖이라 하더라도 "의도적으로 제외" vs "검토 안 함"의 차이가 있다.

---

## Verdict

이 synthesis는 작업 완료의 외양을 갖추고 있지만, 핵심 주장 두 개(OpenAI BLOCKER 단정, fal.ai 1순위 무조건 권장)의 근거가 얇다. BLOCKER 판정은 실측 없는 policy 텍스트 해석에만 기반하고, fal.ai 추천은 데이터 보존 정책과 런웨이 리스크가 공백이다. Task 36 미완 은폐와 위협 모델 맥락 누락까지 포함하면 이 synthesis를 그대로 사용자가 읽고 의사결정하면 두 가지 방향에서 오류가 생길 수 있다: (1) OpenAI API를 쓸 수 있는데 fal.ai로 불필요하게 전환하거나, (2) MVP 품질을 검증됐다고 믿고 Phase A를 배포했다가 렌더링 이슈를 외부 사용자가 발견한다. 수정 권장 — 특히 MAJOR-1, MAJOR-2, MISSING-1 세 항목. 나머지는 Phase A 배포 후 처리 가능하다.
