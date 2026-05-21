"""
계약정서 페이지 나누기 수정 v2
- 3D홈플래너: break 64 제거 → 자동 흐름 (tiny page 제거)
- 약정서(CI,SI): break 118 제거 → 서명란이 제14조와 함께 자연스럽게 흐름
- 기존 나머지 break는 유지
"""
import openpyxl
from openpyxl.worksheet.pagebreak import Break

PATH = r'10-projects/14-hyundaimokdong-marketing/현대목동점_위탁판매_대리점_계약정서_2026.xlsx'
wb = openpyxl.load_workbook(PATH, data_only=False)

def set_row_breaks(ws, break_rows):
    ws.row_breaks.brk.clear()
    for r in break_rows:
        ws.row_breaks.brk.append(Break(id=r, man=True))
    print(f'  [{ws.title}] → break: {break_rows}')

# 3D홈플래너: break 64 제거 (자동 흐름으로 스케일링 후 p1/p2 자연 분리)
set_row_breaks(wb['3D홈플래너 사용권계약서'], [])

# 약정서(CI,SI): 59, 143 유지 / 118 제거 (rows 110-117 tiny page 제거)
set_row_breaks(wb['약정서(CI,SI)'], [59, 143])

# 나머지 유지 (명시적으로 다시 설정)
set_row_breaks(wb['계약서'], [309])
set_row_breaks(wb['약정서(수수료-투자b입점)'], [109])
# 약정서(개인정보), 동반성장: break 없음 (그대로)

wb.save(PATH)
print('\n저장 완료 ✓')
