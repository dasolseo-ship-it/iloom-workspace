---
name: transcript-organizer
description: 녹음 파일(mp3/m4a/wav 등 음성) 또는 텍스트 트랜스크립트(txt)를 자동 분석 및 정리. "녹음 정리", "회의록", "미팅록", "강의 정리", "인터뷰 정리", "녹음파일 요약", "음성 파일 분석", "트랜스크립트" 등 언급 시 자동 실행. 음성→텍스트 변환(Whisper API) 후 인코딩 감지, 내용 분석, 저장까지 완전 자동화.
allowed-tools: Read, Write, PowerShell, Grep, Glob
shell: powershell
---

# Transcript Organizer

긴 녹음 텍스트 파일을 자동으로 분석하고 구조화된 문서로 정리하는 스킬입니다.

## 언제 사용하나요?

- 강의 녹음 파일을 정리할 때
- 미팅 녹음을 회의록으로 만들 때
- 인터뷰 내용을 구조화할 때
- 긴 텍스트 파일(3시간 분량 등)을 요약할 때

## 작동 방식

### Phase 0: 파일 유형 판별 (음성 vs 텍스트)

파일 확장자로 처리 방식을 자동 결정:

| 확장자 | 처리 방식 |
|--------|-----------|
| `.mp3` `.m4a` `.wav` `.mp4` `.webm` `.ogg` `.flac` | Phase 0-A: 음성 → 텍스트 변환 후 Phase 1 진행 |
| `.txt` `.md` | Phase 1: 텍스트 직접 처리 |

#### Phase 0-A: 음성 파일 → 텍스트 변환 (Whisper API)

**필수 환경변수**: `$env:OPENAI_API_KEY`
- 미설정 시 안내: `$env:OPENAI_API_KEY = "sk-..."`

```powershell
# utils/transcribe.ps1 실행
& "${CLAUDE_SKILL_DIR}/utils/transcribe.ps1" -FilePath "[음성파일경로]" -Language "ko"
# 결과: 동일 폴더에 [파일명].txt 생성
```

**지원 형식**: mp3, m4a, wav, mp4, webm, ogg, flac (최대 25MB)

**25MB 초과 시**:
```
파일이 너무 큽니다. 다음 중 선택해주세요:
1. 파일을 분할해서 전달
2. 텍스트 트랜스크립트 파일로 직접 전달
```

변환 완료 후 → 생성된 `.txt` 파일로 Phase 1 진행

---

### Phase 1: 파일 확인 및 인코딩 처리

1. **파일 존재 확인**
   ```powershell
   Test-Path "[파일경로]"
   Get-Item "[파일경로]" | Select-Object Name, Length, LastWriteTime
   ```

2. **인코딩 감지 (BOM 바이트 확인)**
   ```powershell
   $bytes = [System.IO.File]::ReadAllBytes("[파일경로]") | Select-Object -First 4
   # BOM 패턴: FF FE = UTF-16 LE / FE FF = UTF-16 BE / EF BB BF = UTF-8 BOM
   if ($bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) { "UTF-16 LE" }
   elseif ($bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) { "UTF-16 BE" }
   elseif ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB) { "UTF-8 BOM" }
   else { "UTF-8 or ANSI" }
   ```

3. **UTF-16 → UTF-8 자동 변환 (필요시)**
   ```powershell
   $content = [System.IO.File]::ReadAllText("[파일경로]", [System.Text.Encoding]::Unicode)
   $utf8Path = "$env:TEMP\[파일명]-utf8.txt"
   [System.IO.File]::WriteAllText($utf8Path, $content, [System.Text.Encoding]::UTF8)
   ```

4. **파일 크기 확인**
   ```powershell
   $size = (Get-Item "[파일경로]").Length
   Write-Output "$([Math]::Round($size/1KB, 1)) KB"
   ```
   - 110,000 토큰 이상이면 청크 처리 안내

### Phase 2: 컨텍스트 수집

사용자에게 다음 4가지 질문:

1. **유형**: 강의 / 미팅 / 인터뷰?
2. **날짜**: YYYY-MM-DD?
3. **주제**: 간단한 설명 (한 줄)?
4. **저장 위치**:
   - 특정 프로젝트 경로 입력
   - "모름" 또는 "inbox" → `./00-inbox/`

**경로 자동 유추 (파일명/내용 기반)**:
- "팀내", "팀회의", "리테일", "사업팀" → `./20-operations/22-meetings/팀내회의/`
- "대리점", "대구", "가맹점" → `./20-operations/22-meetings/대리점미팅/`
- "소파", "sofa", "TF", "기획" → `./20-operations/22-meetings/소파TF/`
- "외부", "협력사", "거래처", "업체" → `./20-operations/22-meetings/외부미팅/`
- 유추 불가 → `./20-operations/22-meetings/` (루트에 저장)

### Phase 3: 파일 읽기 및 구조 파악

1. **파일 읽기** — Read 툴로 전체 읽기
   - 처음 500줄은 구조 파악용 샘플링일 뿐, **반드시 전체 내용을 끝까지 읽어야 함**
   - 대용량 파일은 여러 번에 걸쳐 읽기 (700줄씩 청크)

2. **구조 분석** (샘플링 단계)
   - 화자 구분 패턴: `발화자 1 (00:00)`
   - 타임스탬프 패턴: `(00:00)`, `[00:00]`
   - 단순 텍스트 (구분 없음)

3. **전체 내용 분석**
   - 전체 파일을 끝까지 읽고 분석
   - 키워드 추출 (자주 등장하는 단어 5~10개)
   - 주제 카테고리 식별

### Phase 4: 내용 분석 및 정리

**유형별 템플릿 적용**:

1. **강의** — [lecture-template.md](templates/lecture-template.md)
   - 개요 (날짜, 강사, 주제, 시간, 특이사항)
   - 핵심 내용 (시간순 또는 주제별)
   - 핵심 요약
   - 다음 작업

2. **미팅** — [meeting-template.md](templates/meeting-template.md)
   - 개요 (날짜, 참석자, 안건, 시간)
   - 안건별 논의 내용
   - 결정 사항
   - Action Items

3. **인터뷰** — [interview-template.md](templates/interview-template.md)
   - 개요 (날짜, 인터뷰 대상, 주제)
   - 주요 질문 및 답변
   - 핵심 인사이트
   - 후속 작업

**정리 원칙**:
- 전체 내용 완전 분석: 처음부터 끝까지 모든 내용을 읽고 정리
- 원본 내용 최대한 보존 (절대 임의로 생략하지 않음)
- 중요 발언은 직접 인용
- 시간 정보 있으면 타임스탬프 포함
- 대용량 파일도 끝까지 읽기: 샘플링은 구조 파악용일 뿐, 실제 정리는 전체 내용 기반

### Phase 5: 문서 생성 및 저장

1. **파일명 생성**
   ```
   YYYY-MM-DD_[주제].md
   ```

2. **저장 경로 결정**
   - 사용자 입력 경로 우선
   - 파일명 유추 경로
   - 기본값: `./00-inbox/`

3. **폴더 생성 및 파일 저장**
   ```powershell
   New-Item -ItemType Directory -Force "[저장경로]"
   # 이후 Write 툴로 저장
   ```

4. **결과 보고**
   ```
   완료!
   파일: [저장경로]/YYYY-MM-DD_[주제].md
   길이: [줄 수]줄
   유형: [강의/미팅/인터뷰]
   ```

## 사용 예시

### 예시 1: 음성 파일 직접 전달
```
사용자: "C:\Users\FURSYS\Downloads\팀회의.m4a 정리해줘"

Claude:
1. .m4a 확인 → Phase 0-A 진행
2. Whisper API로 텍스트 변환 → 팀회의.txt 생성
3. 질문:
   - 유형: 미팅
   - 날짜: 2026-05-12
   - 주제: 팀 주간회의
   - 저장 위치: (파일명에서 "팀회의" 감지) → ./20-operations/22-meetings/팀내회의/
4. 미팅 템플릿 적용
5. 문서 생성: 2026-05-12_팀-주간회의.md
```

### 예시 2: 텍스트 트랜스크립트 정리
```
사용자: "C:\Users\FURSYS\Downloads\인사이터-3주차.txt 이거 강의 정리해줘"

Claude:
1. .txt 확인 → Phase 1 바로 진행
2. UTF-16 감지 → UTF-8 변환
3. 질문 → 강의 템플릿 적용
4. 문서 생성: 2025-10-31_Claude-Code-설치-실습.md
```

### 예시 3: 미팅록 정리
```
사용자: "강릉 프로젝트 미팅 녹음 정리해줘"

Claude:
1. 파일 경로 요청
2. 확장자 확인 → 음성이면 Whisper 변환, 텍스트면 바로 처리
3. 질문 4가지 → 미팅 템플릿 적용
4. 저장: ./20-operations/22-meetings/
```

## 주의사항

### 인코딩 문제 (Windows 기준)
- UTF-16 파일: BOM 바이트 감지 후 자동 변환
- 변환 임시 경로: `$env:TEMP\[파일명]-utf8.txt`
- 변환 실패 시 사용자에게 알림
- EUC-KR 등 다른 인코딩은 수동 확인 필요

### 대용량 파일
- 110,000 토큰 이상: 여러 번 Read로 청크 처리
- 700줄씩 나누어 읽되, 모든 내용을 빠짐없이 분석

### 저장 위치
- 프로젝트 경로 유추 실패 시 inbox 사용
- 사용자가 나중에 수동 정리 가능

### 템플릿 적용
- 화자/타임스탬프 없어도 정리 가능
- 유형별 템플릿은 가이드일 뿐, 내용에 맞게 유연하게 조정

## 워크플로우 요약

```
0. 파일 유형 판별 (음성 vs 텍스트)
   └─ 음성 → Whisper API 변환 (utils/transcribe.ps1)
   └─ 텍스트 → 인코딩 감지 → UTF-8 변환
1. 사용자 질문 (4개)
2. 파일 구조 파악 (Read 툴, 전체 읽기)
3. 템플릿 적용 및 정리
4. 문서 저장 및 보고
```

## 환경변수 설정 가이드

```powershell
# OpenAI API 키 (음성 변환 필수)
$env:OPENAI_API_KEY = "sk-..."

# 영구 설정 (선택)
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

---

**Version**: 1.2.0 (음성 파일 지원 추가)
**Created**: 2025-11-01
**Updated**: 2026-05-12
