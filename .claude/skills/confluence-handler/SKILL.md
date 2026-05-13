---
name: confluence-handler
description: Confluence 페이지/스페이스 관리. "컨플루언스", "Confluence", "페이지 만들어", "위키", "문서 작성", "스페이스 조회", "Confluence에 저장" 등을 언급하면 자동 실행.
allowed-tools: Bash, PowerShell, Read, Write
shell: powershell
---

# Confluence Handler Skill

## Prerequisites

### 필수 환경변수 (세션 시작 시 설정)
```powershell
$env:CONFLUENCE_URL   = "https://fursys.atlassian.net"
$env:CONFLUENCE_EMAIL = "dasol_seo@fursys.com"
$env:CONFLUENCE_TOKEN = "your_api_token"
```

### 스크립트 경로
```
${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1
```

---

## 사용법

모든 기능은 아래 스크립트로 실행합니다:
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" <command> [options]
```

---

## 기능 목록

### 스페이스 관리

#### 스페이스 목록 조회
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-spaces
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-spaces -Limit 50
```

#### 스페이스 상세 조회
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" get-space -SpaceKey "sales01"
```

---

### 페이지 관리

#### 스페이스 내 페이지 목록
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-pages -SpaceKey "sales01"
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-pages -SpaceKey "sales01" -Limit 50
```

#### 페이지 내용 조회
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" get-page -PageId "123456789"
```

#### 제목으로 페이지 검색
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" get-page-by-title -SpaceKey "sales01" -Title "월간 보고"
```

#### 페이지 생성
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" create-page `
  -SpaceKey "sales01" `
  -Title "페이지 제목" `
  -Body "<p>내용을 입력하세요.</p><h2>섹션 제목</h2><p>섹션 내용</p>"

# 하위 페이지로 생성
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" create-page `
  -SpaceKey "sales01" `
  -Title "하위 페이지 제목" `
  -Body "<p>내용</p>" `
  -ParentId "부모_페이지_ID"
```

#### 페이지 수정
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" update-page `
  -PageId "123456789" `
  -Title "수정된 제목" `
  -Body "<p>수정된 내용</p>"
```

#### 페이지 삭제
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" delete-page -PageId "123456789"
```

#### 하위 페이지 목록
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" get-children -PageId "123456789"
```

---

### 블로그 포스트

#### 블로그 목록
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-blogs -SpaceKey "sales01"
```

#### 블로그 작성
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" create-blog `
  -SpaceKey "sales01" `
  -Title "블로그 제목" `
  -Body "<p>블로그 내용</p>"
```

---

### 검색 (CQL)

```powershell
# 제목 검색
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" search -Query "title~'검색어'"

# 특정 스페이스에서 검색
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" search -Query "space=sales01 AND title~'월간'"

# 최근 수정된 페이지
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" search -Query "space=sales01 AND lastModified>'2026-01-01'"

# 레이블로 검색
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" search -Query "label=중요 AND space=sales01"
```

---

### 댓글

#### 댓글 목록
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-comments -PageId "123456789"
```

#### 댓글 추가
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" add-comment `
  -PageId "123456789" `
  -Comment "댓글 내용을 입력하세요"
```

---

### 레이블

#### 레이블 조회
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" get-labels -PageId "123456789"
```

#### 레이블 추가
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" add-label -PageId "123456789" -Label "중요"
```

#### 레이블 삭제
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" remove-label -PageId "123456789" -Label "중요"
```

---

### 첨부파일

#### 첨부파일 목록
```powershell
& "${CLAUDE_SKILL_DIR}/scripts/confluence_api.ps1" list-attachments -PageId "123456789"
```

---

## Body HTML 작성 가이드

Confluence Storage Format 기준:

| 요소 | HTML |
|------|------|
| 제목 1 | `<h1>제목</h1>` |
| 제목 2 | `<h2>제목</h2>` |
| 단락 | `<p>내용</p>` |
| 굵게 | `<strong>텍스트</strong>` |
| 기울임 | `<em>텍스트</em>` |
| 글머리 목록 | `<ul><li>항목</li></ul>` |
| 번호 목록 | `<ol><li>항목</li></ol>` |
| 표 | `<table><tbody><tr><th>헤더</th></tr><tr><td>내용</td></tr></tbody></table>` |
| 코드 | `<code>코드</code>` |
| 링크 | `<a href="URL">텍스트</a>` |
| 구분선 | `<hr/>` |

---

## 스페이스 키 참조 (fursys.atlassian.net)

주요 스페이스는 `list-spaces` 명령으로 확인.

---

## 보안

- 토큰은 반드시 환경변수(`$env:CONFLUENCE_TOKEN`)로 관리
- 코드나 문서에 하드코딩 금지
- 민감한 페이지 삭제 시 반드시 확인 후 실행

---

## Version History

- **v1.0.0 (2026-05-12)**: 초기 작성 — 스페이스/페이지/블로그/검색/댓글/레이블/첨부파일 지원 (PowerShell 기반)
