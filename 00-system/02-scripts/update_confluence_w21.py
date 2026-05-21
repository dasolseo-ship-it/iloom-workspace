# -*- coding: utf-8 -*-
"""
Confluence 주간업무계획 W21 업데이트 스크립트
페이지 ID: 906210046 (주간업무계획(5월 3주차) _ 5월 15일 ~ 5월 21일)
서다솔 담당 행 금주진행업무 + 익주진행계획 업데이트
"""

import urllib.request
import base64
import json
import os
import sys

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')
page_id = '906210046'

if not token:
    print("❌ CONFLUENCE_TOKEN 환경변수가 설정되지 않았습니다.")
    print("   실행 전: $env:CONFLUENCE_TOKEN = 'your_token'")
    exit(1)

creds = base64.b64encode(f'{email}:{token}'.encode()).decode()
headers = {
    'Authorization': f'Basic {creds}',
    'Content-Type': 'application/json'
}

# 현재 페이지 가져오기
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
    print("서다솔을 찾지 못했습니다!")
    exit(1)

tr_start = html.rfind('<tr', 0, idx_dasol)
tr_end = html.find('</tr>', idx_dasol) + 5
print(f"서다솔 행: {tr_start} ~ {tr_end}")

# 기존 행에서 담당자 td 끝 위치 찾기
row_html = html[tr_start:tr_end]
dasol_marker = '서다솔</p></td>'
idx_marker = row_html.find(dasol_marker)
if idx_marker < 0:
    print("서다솔 td 마커를 찾지 못했습니다!")
    print("실제 내용 확인:", row_html[row_html.find('서다솔')-50:row_html.find('서다솔')+100])
    exit(1)

prefix = row_html[:idx_marker + len(dasol_marker)]
print("앞부분 추출 완료")

# 새 금주 진행 업무 td
new_current_week_td = '''<td><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-01"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 온오프 보전 시스템 킥오프 (05.19)</p><ac:task-list>
<ac:task>
<ac:task-id>301</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">김선우 어드바이저 킥오프 회의, PRD 확정</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>302</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">온라인→오프라인 수주취소 5% 보전 정책 확정, 개발 데드라인 6월 첫째주</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-02"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 담당매장 외근 (05.20)</p><ac:task-list>
<ac:task>
<ac:task-id>303</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">롯데영등포점 외근 (11:00~14:30)</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>304</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">롯데구리점 외근 (14:30~17:30)</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-03"><ac:parameter ac:name="title">진행중</ac:parameter><ac:parameter ac:name="colour">Yellow</ac:parameter></ac:structured-macro> 현대목동점 위탁판매 대리점 계약정서 작성 (05.21)</p><ac:task-list>
<ac:task>
<ac:task-id>305</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">사업자등록증 확인 (페드라 / 안중우 / 417-10-72598)</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>306</ac:task-id>
<ac:task-status>complete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">계약기간 2026.05.01~2027.03.31, 엑셀 계약정서 5개 시트 작업</span></ac:task-body>
</ac:task>
<ac:task>
<ac:task-id>307</ac:task-id>
<ac:task-status>incomplete</ac:task-status>
<ac:task-body><span class="placeholder-inline-tasks">일부 시트 오류 수정 중 (05.22 완료 예정)</span></ac:task-body>
</ac:task>
</ac:task-list><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-04"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 롯데바이오로직스 임직원 공동구매 합의서 작성</p><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-05"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 현대목동점 임직원 할인 홍보 시안 제작</p><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-06"><ac:parameter ac:name="title">완료</ac:parameter><ac:parameter ac:name="colour">Blue</ac:parameter></ac:structured-macro> 현대목동점 재산종합보험 서류 등록</p></td>'''

# 새 익주 진행 계획 td
new_next_week_td = '''<td><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-07"><ac:parameter ac:name="title">진행예정</ac:parameter><ac:parameter ac:name="colour">Green</ac:parameter></ac:structured-macro> 현대목동점 계약정서 오류 수정 완료</p><p><ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="ds-w21-08"><ac:parameter ac:name="title">진행예정</ac:parameter><ac:parameter ac:name="colour">Green</ac:parameter></ac:structured-macro> 온오프 보전 시스템 개발 진행</p></td>'''

# 새 행 조합 (앞부분 + 금주 + 익주 + 비고 + tr 닫기)
new_row = prefix + new_current_week_td + new_next_week_td + '<td><p /></td></tr>'

# HTML 전체에서 기존 행 교체
new_html = html[:tr_start] + new_row + html[tr_end:]

print(f"HTML 수정 완료 (기존 {len(html)} → 새 {len(new_html)} 글자)")

# Confluence API PUT 요청
payload = json.dumps({
    'version': {'number': version + 1},
    'title': title,
    'type': 'page',
    'body': {
        'storage': {
            'value': new_html,
            'representation': 'storage'
        }
    }
}, ensure_ascii=False).encode('utf-8')

put_req = urllib.request.Request(
    f'{url_base}/wiki/rest/api/content/{page_id}',
    data=payload,
    headers=headers,
    method='PUT'
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
