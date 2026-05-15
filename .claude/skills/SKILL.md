---
name: excel-analyzer
description: 엑셀 파일 자동 분석. "엑셀 분석", "excel 분석", "xlsx 분석", "데이터 분석해줘", "엑셀 파일 분석", "csv 변환", "폴더 분석" 등을 언급하거나 .xlsx/.xls 파일 경로를 제공하면 자동 실행. 폴더 내 전체 엑셀 변환 → 시트별 CSV 저장 → AI 분석 → 마크다운 리포트까지 전체 자동화.
allowed-tools: Bash, Read, Write, Glob
---

# 엑셀 데이터 분석 스킬

폴더 내 모든 엑셀 파일(.xlsx/.xls)을 시트별 CSV로 변환하고, AI가 데이터를 분석하여 인사이트와 액션 아이템까지 도출하는 End-to-End 자동화 스킬.

**전용 스크립트**:
- `scripts/excel_to_csv.py` – 엑셀 → 시트별 CSV 변환
- `scripts/analyze_data.py` – CSV 데이터 분석 + 마크다운 리포트 생성

## 전체 워크플로우

```
[1] 입력 경로 확인 (폴더 또는 파일)
       ↓
[2] excel_to_csv.py: 모든 .xlsx/.xls → 시트별 CSV 변환
       ↓
[3] 변환된 CSV 목록 확인
       ↓
[4] analyze_data.py: 데이터 구조 파악 + 통계 집계
       ↓
[5] AI 분석: 인사이트 도출 + 액션 아이템 제안
       ↓
[6] 마크다운 리포트 저장
```

---

## Step 1: 입력 경로 확인

### 폴더가 제공된 경우
```
사용자: "이 폴더 분석해줘 10-projects/11-대리점/"
→ 해당 폴더 내 모든 .xlsx/.xls 자동 탐색
```

### 파일이 직접 제공된 경우
```
사용자: "경쟁사합본.xlsx 분석해줘"
→ 해당 파일만 처리 (파일의 부모 폴더 기준)
```

### 경로 미제공 시
현재 워크스페이스 루트를 기본 경로로 사용하되, 사용자에게 확인 요청.

---

## Step 2: 엑셀 → CSV 변환 (excel_to_csv.py)

```bash
python ".claude/skills/excel-analyzer/scripts/excel_to_csv.py" "[폴더경로]"
```

**출력 파일 명명 규칙:**
```
원본파일명_시트명.csv
예) 경쟁사합본_시트1.csv, 경쟁사합본_대리점현황.csv
```

**특징:**
- 폴더 내 모든 `.xlsx`, `.xls` 자동 탐색
- 시트별로 개별 CSV 파일 생성
- 인코딩: UTF-8-BOM (Excel에서 바로 열기 가능)
- 이미 변환된 파일 덮어쓰기 (타임스탬프 없이)

**예상 결과:**
```
변환 완료: 경쟁사합본.xlsx (3개 시트)
  → 경쟁사합본_시트1.csv (245행)
  → 경쟁사합본_대리점현황.csv (89행)
  → 경쟁사합본_요약.csv (12행)
```

---

## Step 3: 변환 결과 확인

변환된 CSV 파일 목록과 행수 확인 후 분석 진행 여부 결정.

---

## Step 4: 데이터 분석 (analyze_data.py)

```bash
python ".claude/skills/excel-analyzer/scripts/analyze_data.py" "[CSV파일 또는 폴더]"
```

**분석 항목:**
- 파일 개요: 행수, 열수, 컬럼 목록
- 숫자 컬럼: 합계, 평균, 최대/최소, 결측값
- 텍스트 컬럼: 고유값 개수, 상위 5개 값
- 날짜 컬럼: 범위, 분포

**출력:** `분석리포트_{YYYYMMDD}.md` (동일 폴더에 저장)

---

## Step 5: AI 인사이트 도출

analyze_data.py 결과를 바탕으로 AI가 추가 분석:

### 비즈니스 인사이트
- 주요 패턴 및 트렌드
- 이상치 또는 주목할 수치
- 경쟁사/매출/상권 관련 시사점

### 액션 아이템
- 즉시 실행 가능한 것 (이번 주)
- 중기 과제 (이번 달)
- 검토가 필요한 사항

---

## Step 6: 리포트 저장

### 저장 위치
엑셀 파일과 동일한 폴더 또는 `30-knowledge/` 하위에 저장.

### 파일명
```
분석리포트_{원본파일명}_{YYYYMMDD}.md
```

### 리포트 구조
```markdown
# 데이터 분석 리포트: [파일명]

## 요약
## 데이터 개요
## 주요 통계
## 핵심 인사이트
## 액션 아이템
## 부록: 컬럼 상세
```

---

## 사용 예시

### 예시 1: 폴더 전체 분석
```
사용자: "10-projects/11-대리점/ 폴더 엑셀 분석해줘"

Claude:
1. 폴더 내 xlsx/xls 탐색 → 경쟁사합본.xlsx 발견
2. excel_to_csv.py 실행 → 시트별 CSV 3개 생성
3. analyze_data.py 실행 → 통계 집계
4. AI 인사이트 + 액션 아이템 도출
5. 분석리포트_경쟁사합본_20260218.md 저장
```

### 예시 2: 파일 직접 지정
```
사용자: "경쟁사합본.xlsx 분석해줘"
→ 해당 파일만 처리
```

### 예시 3: 경로 없이 요청
```
사용자: "엑셀 분석해줘"
→ 경로 확인 요청 후 진행
```

---

## 트러블슈팅

### openpyxl 패키지 없음
```bash
pip install openpyxl xlrd pandas numpy
```

### .xls 파일 오류 (xlrd 필요)
```bash
pip install xlrd==1.2.0
```
> xlrd 2.x는 .xls만 지원. .xlsx는 openpyxl 사용.

### 한글 깨짐
- 변환 파일은 UTF-8-BOM으로 저장됨
- Excel에서 열 때 자동 인식

---

## 의존성

```
pip install openpyxl xlrd pandas numpy
```

## 파일 구조

```
excel-analyzer/
├── SKILL.md                    # 이 파일 (SOP)
└── scripts/
    ├── excel_to_csv.py         # 엑셀 → CSV 변환
    ├── analyze_data.py         # 데이터 분석 + 리포트
    └── requirements.txt        # 의존성 목록
```

---

## 버전 히스토리

- **v1.0.0 (2026-02-18)**: 초기 스킬 생성
  - 폴더 전체 일괄 변환
  - 시트별 CSV 저장
  - 마크다운 리포트 자동 생성
