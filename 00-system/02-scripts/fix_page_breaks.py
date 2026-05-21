"""
계약정서 페이지 나누기 정비
- 절 중간, 테이블 중간 나누기 제거
- 논리적 섹션 경계(조항 끝)에만 나누기 설정
"""
import openpyxl
from openpyxl.worksheet.pagebreak import Break

PATH = r'c:\Users\FURSYS\Downloads\iloom-workspace-claude\10-projects\14-hyundaimokdong-marketing\현대목동점_위탁판매_대리점_계약정서_2026.xlsx'

wb = openpyxl.load_workbook(PATH, data_only=False)

def set_row_breaks(ws, break_rows):
    """기존 나누기 전부 제거 후 지정 행에만 설정"""
    ws.row_breaks.brk.clear()
    for r in break_rows:
        ws.row_breaks.brk.append(Break(id=r, man=True))
    print(f'  [{ws.title}] → 나누기: {break_rows}')

# ── 계약서 ──
# 313행(제26조 중간) → 309행(제25조 끝, 제26조 시작 전)
set_row_breaks(wb['계약서'], [309])

# ── 약정서(수수료-투자b입점) ──
# 82행(제8조 테이블 중간) → 109행(제10조 끝, 서명란 시작 전)
set_row_breaks(wb['약정서(수수료-투자b입점)'], [109])

# ── 약정서(CI,SI) ──
# 170행(별첨2 중간) 제거 / 59, 118 유지
# 143행(서명란 끝, 별첨1 시작 전) 추가
set_row_breaks(wb['약정서(CI,SI)'], [59, 118, 143])

# ── 나머지 시트는 현재 설정 유지 ──
# 약정서(개인정보): 나누기 없음, 자동 2페이지
# 3D홈플래너: 64행 유지
# 동반성장: 나누기 없음, 1페이지

wb.save(PATH)
print('\n저장 완료 ✓')
