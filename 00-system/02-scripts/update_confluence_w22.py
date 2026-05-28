# -*- coding: utf-8 -*-
"""
Confluence 주간업무계획 W22 업데이트 스크립트
페이지 ID: 906311582 (주간업무계획(5월 4주차) _ 5월 22일 ~ 5월 28일)
서다솔 담당 행 금주진행업무 + 익주진행계획 업데이트
"""
import urllib.request, base64, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')
page_id = '906311582'

if not token:
    print("❌ CONFLUENCE_TOKEN 환경변수 없음")
    sys.exit(1)

creds = base64.b64encode(f'{email}:{token}'.encode()).decode()
headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}

print("페이지 불러오는 중...")
req = urllib.request.Request(
    f'{url_base}/wiki/rest/api/content/{page_id}?expand=body.storage,version',
    headers=headers
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

html = data['body']['storage']['value']
version = data['version']['number']
title = data['title']
print(f"버전: {version}, 제목: {title}")

# 서다솔 행 찾기
idx_dasol = html.find('서다솔')
if idx_dasol < 0:
    print("❌ 서다솔 행 없음")
    sys.exit(1)

tr_start = html.rfind('<tr', 0, idx_dasol)
tr_end = html.find('</tr>', idx_dasol) + 5
print(f"서다솔 행: {tr_start} ~ {tr_end}")

row_html = html[tr_start:tr_end]
dasol_marker = '서다솔</p></td>'
idx_marker = row_html.find(dasol_marker)
if idx_marker < 0:
    print("❌ 서다솔 td 마커 없음")
    print("실제 내용:", row_html[row_html.find('서다솔')-30:row_html.find('서다솔')+80])
    sys.exit(1)

prefix = row_html[:idx_marker + len(dasol_marker)]
print("앞부분 추출 완료")

# 금주 진행 업무 (W22: 5/22~5/28)
new_current_week_td = '''<td><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-01"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 온오프 보전 시스템 데이터 매칭 아키텍처 탐색 (05.22)</p><ac:task-list>
<ac:task>
<ac:task-id>401</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">ERP 엑셀 export 분석 — 주소·이름 포함, 휴대폰 미포함 확인</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>402</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">매칭 키 확정: 이름 + 주소(동까지) + 휴대폰 뒷 4자리</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-02"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 롯데영등포점 B2B 협조전 작성 (05.26)</p><ac:task-list>
<ac:task>
<ac:task-id>403</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">구세군작업장 21% 할인 협조전 및 할인공급요청서 작성</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-03"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 온오프 보전 시스템 기능 개발 (05.26)</p><ac:task-list>
<ac:task>
<ac:task-id>404</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">엑셀 내보내기 API 개발 (GET /api/orders/export)</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>405</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">매장별 집계 API 개발 (GET /api/stats/by-store)</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-04"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 롯데인천2점 팝업 계약연장 품의서 및 계약정서 작성 (05.27)</p><ac:task-list>
<ac:task>
<ac:task-id>406</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">계약연장 기간: ~2026.07.31, 품의서 및 계약정서 작성 완료</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-05"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 현대목동점 인테리어 설치 합의서 회신 (05.28)</p><ac:task-list>
<ac:task>
<ac:task-id>407</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">공사범위별 금액 정리 회신 (총 88,658,000원 / VAT별도)</span></ac:task-body>
</ac:task>
</ac:task-list></td>'''

# 익주 진행 계획
new_next_week_td = '''<td><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-06"><ac:parameter ac:name="title">진행예정</ac:parameter><ac:parameter ac:name="colour">Green</ac:parameter></ac:structured-macro> 온오프 보전 시스템 — 데이터 파이프라인 설계</p><ac:task-list>
<ac:task>
<ac:task-id>408</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">선우님 확인: 휴대폰 뒷 4자리 출처 및 bulk export 가능 여부</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>409</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">자동 매칭 파이프라인 설계 착수</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w22-07"><ac:parameter ac:name="title">진행예정</ac:parameter><ac:parameter ac:name="colour">Green</ac:parameter></ac:structured-macro> 온오프 보전 시스템 추가 기능 개발 (지급 상태 관리, 월별 정산)</p></td>'''

new_row = prefix + new_current_week_td + new_next_week_td + '<td><p /></td></tr>'
new_html = html[:tr_start] + new_row + html[tr_end:]
print(f"HTML 수정 완료 (기존 {len(html)} → 새 {len(new_html)} 글자)")

payload = json.dumps({
    'version': {'number': version + 1},
    'title': title,
    'type': 'page',
    'body': {'storage': {'value': new_html, 'representation': 'storage'}}
}, ensure_ascii=False).encode('utf-8')

put_req = urllib.request.Request(
    f'{url_base}/wiki/rest/api/content/{page_id}',
    data=payload, headers=headers, method='PUT'
)

try:
    with urllib.request.urlopen(put_req) as resp:
        result = json.loads(resp.read())
        print(f"\n✅ 업데이트 성공!")
        print(f"새 버전: {result['version']['number']}")
        print(f"링크: https://fursys.atlassian.net/wiki{result['_links']['webui']}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f"❌ 오류 {e.code}: {e.reason}")
    print(body[:500])
