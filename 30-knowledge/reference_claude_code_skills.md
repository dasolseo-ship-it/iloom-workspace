---
name: claude-code-skills-guide
description: "Claude Code Skills 공식 문서 정리 — 개념, 파일 구조, frontmatter 필드, best practices, settings.json 설정"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 86af5cfc-2cf1-44c4-ab81-bd21a21c342e
---

# Claude Code Skills 완벽 가이드

조사일: 2026-05-12

---

## 1. Skills란?

Skills는 Claude Code를 확장하는 재사용 가능한 명령어. `.SKILL.md` 파일에 지시사항을 작성하면 Claude가 도구로 활용.

### Skills vs CLAUDE.md vs Auto Memory

| 항목 | Skills | CLAUDE.md | Auto Memory |
|------|--------|-----------|-------------|
| 작성자 | 사용자 | 사용자 | Claude |
| 언제 로드 | 호출할 때만 | 모든 세션 시작 | 모든 세션 시작 |
| 컨텍스트 비용 | 낮음 | 높음 | 중간 |

---

## 2. 파일 구조 및 위치

### 최소 구조
```
~/.claude/skills/skill-name/
└── SKILL.md   # 필수
```

### 위치별 범위

| 위치 | 경로 | 범위 |
|------|------|------|
| 개인 | `~/.claude/skills/<name>/SKILL.md` | 모든 프로젝트 |
| 프로젝트 | `.claude/skills/<name>/SKILL.md` | 해당 프로젝트만 (Git 공유 가능) |
| 플러그인 | `<plugin>/skills/<name>/SKILL.md` | 플러그인 활성화 시 |
| 엔터프라이즈 | 관리 설정 위치 | 조직 전체 |

**우선순위**: 엔터프라이즈 > 개인 > 프로젝트 > 플러그인

---

## 3. SKILL.md 문법

### 기본 구조
```yaml
---
name: skill-name
description: 스킬 기능 및 사용 시기 설명 (1,536자 제한)
---

지시사항...
```

### 전체 Frontmatter 필드

| 필드 | 설명 |
|------|------|
| `name` | 표시 이름 (소문자/숫자/하이픈, 최대 64자) |
| `description` | 기능 및 사용 시기 (1,536자 제한, 필수 권장) |
| `when_to_use` | 추가 사용 시기 (description에 병합) |
| `argument-hint` | 자동완성 힌트 (예: `[issue-number]`) |
| `arguments` | 위치 인수 목록 |
| `disable-model-invocation` | `true`면 수동 호출만 가능 |
| `user-invocable` | `false`면 `/` 메뉴에서 숨김 |
| `allowed-tools` | 사전 승인 도구 목록 |
| `model` | 실행 모델 지정 |
| `effort` | 노력 수준: `low/medium/high/xhigh/max` |
| `context` | `fork`면 서브에이전트에서 실행 |
| `agent` | `context: fork`일 때 에이전트 타입 |
| `hooks` | 라이프사이클 훅 |
| `paths` | 글로브 패턴 자동 활성화 조건 |
| `shell` | `bash` (기본) 또는 `powershell` |

### 인수 참조 변수

| 변수 | 설명 |
|------|------|
| `$ARGUMENTS` | 전달된 모든 인수 |
| `$ARGUMENTS[N]` or `$N` | N번째 인수 |
| `$name` | 명명 인수 |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |
| `${CLAUDE_SKILL_DIR}` | 스킬 디렉토리 경로 |

---

## 4. 동적 컨텍스트 주입

```markdown
## 현재 변경사항
!`git diff HEAD`

## 환경 정보
```!
node --version
git status --short
```
```

명령이 즉시 실행되어 출력이 프롬프트에 삽입됨.

---

## 5. Best Practices

### Description 작성
- 첫 문장에 핵심 사용 사례 기술
- 언제 Claude가 자동 호출해야 하는지 명확히
- 1,536자 이내

```yaml
# ❌ 나쁜 예
description: General skill for code things

# ✅ 좋은 예
description: Summarizes uncommitted changes and flags risky changes. Use when asking what changed or wanting a commit message.
```

### 호출 방식 선택

| 시나리오 | 설정 |
|---------|------|
| 커밋, 배포, 메시지 발송 (부작용 있음) | `disable-model-invocation: true` |
| API 가이드, 컨벤션 (참고 자료) | 기본값 (자동 호출) |
| 배경 지식 (사용자 입력 아님) | `user-invocable: false` |

### 파일 크기 관리
- `SKILL.md`: 500줄 이내
- 상세 내용은 `reference.md`, `examples.md`로 분리
- SKILL.md는 개요 + 보조 파일 링크에 집중

### allowed-tools
- 필요한 최소 도구만 나열
- deny 규칙은 여전히 적용됨 (사전 승인이지 권한 우회 아님)

---

## 6. 사용 방법

```bash
# 수동 호출
/skill-name

# 인수 전달
/skill-name argument1 argument2

# 메뉴 확인
/skills
```

Claude가 description을 보고 자동 호출하기도 함.

---

## 7. settings.json 관련 설정

```json
{
  "skillListingBudgetFraction": 0.01,
  "maxSkillDescriptionChars": 1536,
  "skillOverrides": {
    "legacy-skill": "name-only",
    "unused-skill": "off",
    "manual-only": "user-invocable-only"
  },
  "disableSkillShellExecution": false
}
```

### skillOverrides 값

| 값 | Claude 자동 호출 | `/` 메뉴 |
|----|----------------|---------|
| `"on"` (기본) | 가능 | 표시 |
| `"name-only"` | 이름만 보임 | 표시 |
| `"user-invocable-only"` | 불가 | 표시 |
| `"off"` | 불가 | 숨김 |

### 문제 해결
- `/doctor` 실행 → truncation 상태 확인
- 많이 쓰는 skill은 `skillOverrides`에서 우선순위 올리기
- 설명이 잘리면 `skillListingBudgetFraction` 증가

---

## 8. 실용 예제

### 변경사항 요약
```yaml
---
name: summarize-changes
description: Summarizes uncommitted changes and flags anything risky.
---
## Current changes
!`git diff HEAD`

Summarize in 2-3 bullets and list risks.
```

### GitHub 이슈 수정
```yaml
---
name: fix-issue
disable-model-invocation: true
arguments: [issue-number]
allowed-tools:
  - Bash(gh issue view *)
  - Bash(npm test)
---
# Fix Issue #$0
!`gh issue view $0`
Implement fix following standards in [standards.md](standards.md).
```

### 서브에이전트 조사
```yaml
---
name: deep-research
context: fork
agent: Explore
---
Research: $ARGUMENTS
1. Glob/Grep 관련 파일 탐색
2. 핵심 파일 분석
3. 결과 보고
```

---

## 9. 공식 문서 링크

- Skills 전체 가이드: https://code.claude.com/docs/en/skills.md
- 메모리/CLAUDE.md: https://code.claude.com/docs/en/memory.md
- Subagents: https://code.claude.com/docs/en/subagents.md
- 권한 설정: https://code.claude.com/docs/en/permissions.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Settings: https://code.claude.com/docs/en/settings.md
