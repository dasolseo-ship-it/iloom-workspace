"""
현대목동점 계약정서 — 인쇄영역/페이지 설정 정비
- A4 세로, 가로 1페이지 너비 맞춤
- 여백 상하 1.8cm / 좌우 1.5cm
- 수평 가운데 정렬
- 기존 페이지 나누기 유지
"""
import openpyxl
from openpyxl.worksheet.page import PageMargins

PATH = r'c:\Users\FURSYS\Downloads\iloom-workspace-claude\10-projects\14-hyundaimokdong-marketing\현대목동점_위탁판매_대리점_계약정서_2026.xlsx'

# 계약 관련 출력 시트 + 인쇄 범위
SHEETS = {
    '계약서':                    'A1:K339',
    '약정서(수수료-투자b입점)':   'A1:K146',
    '약정서(CI,SI)':             'A1:J185',
    '약정서(개인정보)':           'A1:J93',
    '3D홈플래너 사용권계약서':    'A1:K112',
    '동반성장 및 청렴서약서':     'A1:J44',
}

# 여백: 1.5cm 좌우 ≈ 0.59", 1.8cm 상하 ≈ 0.71"
MARGINS = PageMargins(
    left=0.59, right=0.59,
    top=0.71,  bottom=0.71,
    header=0.3, footer=0.3
)

wb = openpyxl.load_workbook(PATH, data_only=False)

for name, print_area in SHEETS.items():
    ws = wb[name]

    # 인쇄 영역
    ws.print_area = print_area

    # 용지: A4(9), 세로
    ws.page_setup.paperSize  = 9
    ws.page_setup.orientation = 'portrait'

    # 가로 1페이지 너비 맞춤 (세로는 자동 흐름)
    ws.page_setup.fitToWidth  = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.scale       = None   # fitToWidth 사용 시 scale 무효화

    # fitToPage 활성화
    if ws.sheet_properties.pageSetUpPr is None:
        from openpyxl.worksheet.properties import PageSetupProperties
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    else:
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    # 여백
    ws.page_margins = MARGINS

    # 수평 가운데
    ws.print_options.horizontalCentered = True

    print(f'  [{name}] 인쇄영역={print_area} ✓')

wb.save(PATH)
print('\n저장 완료 ✓')
