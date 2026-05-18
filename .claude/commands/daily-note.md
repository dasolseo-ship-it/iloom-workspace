---
description: 오늘 날짜의 Daily Note 생성 또는 열기
allowed-tools: Read, Write, Edit, Bash, PowerShell
---

오늘 날짜의 Daily Note를 생성하거나 열어주세요.

**수행할 작업:**

1. 오늘 날짜 확인 (YYYY-MM-DD 형식)

2. **캘린더 일정 가져오기 (gogcli)**
   - PowerShell로 실행:
     ```powershell
     $env:GOG_KEYRING_PASSWORD = "gog1234"; gog --account dasol7253@gmail.com calendar events list --today
     ```
   - 결과에서 START, END, SUMMARY 파싱
   - 시간대(+09:00) 제거하고 HH:MM 형식으로 변환
   - 오전(~12:00) / 오후(12:00~) / 저녁(18:00~) 으로 분류
   - 조회 실패 시 무시하고 계속 진행

3. 경로:
   - 파일 경로: `./40-personal/41-daily/YYYY-MM-DD.md`

4. 파일이 없으면:
   - 아래 구조로 새 파일 생성 (날짜 직접 계산):
     - `{{date}}`: 오늘 날짜 (YYYY-MM-DD)
     - `{{weekday}}`: 오늘 요일 (월요일~일요일)
     - `{{yesterday}}`: 어제 날짜
     - `{{tomorrow}}`: 내일 날짜
     - `{{week}}`: ISO 주차 (YYYY-Www)
   - 캘린더 일정이 있으면:
     - `## 오늘의 집중` 섹션에 일정 항목 추가 (체크박스)
     - `### 오전` / `### 오후` / `### 저녁` 에 시간+일정명 삽입
     - `## 미팅 / 통화` 테이블에 시간/내용 행 삽입

5. 파일이 있으면:
   - 현재 내용 확인
   - 캘린더에서 가져온 일정 중 아직 노트에 없는 항목만 추가
   - 추가한 내용 요약해서 알려주기
