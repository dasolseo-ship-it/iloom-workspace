# PROGRESS - 매출기여 보전 프로그램

## 2026-05-18 — 초기 개발

### 완료
- [x] 프로젝트 구조 설계
- [x] FastAPI 백엔드 구현 (`app.py`)
  - 행사 CRUD API
  - 수주 입력 + 매칭 엔진
  - 커넥트플러스 Excel 업로드 API
  - 통계 API
- [x] 프론트엔드 UI (`templates/index.html`)
  - 행사 관리 탭
  - 수주 입력 + 실시간 결과 표시 탭
  - 결과 조회/필터 탭
  - 누적 통계 바

### 매칭 로직 구현 내용
- 동일 시리즈 + 동일 품목 체크
- 예외 규칙: 쿠시노 ≠ 쿠시노코지, 로이 ≠ 로이모노
- D-1 등록일 자동 체크
- 부분인정 시 전체 결제액 5% 적용 (배분 기준 정책 미정으로 별도 안내)

### 다음 단계 (TODO)
- [ ] 커넥트플러스 실제 Excel 내보내기 형식 확인 후 파서 조정
- [ ] 보전금 지급 처리 상태 추가 (미지급/지급완료)
- [ ] 월별/매장별 통계 리포트
- [ ] Excel 결과 내보내기

### 블로커
- Python 미설치 상태 → winget install Python.Python.3.12 필요

## 실행 명령
```powershell
cd "C:\Users\FURSYS\Downloads\iloom-workspace-claude\10-projects\매출기여-보전프로그램"
pip install -r requirements.txt
python app.py
# → http://localhost:8000
```
