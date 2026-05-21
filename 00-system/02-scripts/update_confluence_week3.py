# -*- coding: utf-8 -*-
"""
Confluence 주간회의 3주차 업데이트
- 2주차 서다솔 차주업무계획 → 3주차 금주업무실적으로 이식
- 이번 주 추가 실적 반영
페이지 ID: 3155297702 (2026년 5월 3주차 5/18~5/22)
"""

import urllib.request
import base64
import json
import os
import re

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')

if not token:
    print("❌ CONFLUENCE_TOKEN 환경변수가 설정되지 않았습니다.")
    print("   실행 전: $env:CONFLUENCE_TOKEN = 'your_token'")
    exit(1)

page_id_week2 = '3155297691'
page_id_week3 = '3155297702'

creds = base64.b64encode(f'{email}:{token}'.encode()).decode()
headers = {
    'Authorization': f'Basic {creds}',
    'Content-Type': 'application/json'
}

def fetch_page(page_id):
    req = urllib.request.Request(
        f'{url_base}/wiki/rest/api/content/{page_id}?expand=body.storage,version',
        headers=headers
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def split_tds(row_html):
    """row html에서 td 목록 반환 [(start, end, html), ...]"""
    tds = []
    p = 0
    while True:
        s = row_html.find('<td', p)
        if s < 0: break
        e = row_html.find('</td>', s) + 5
        tds.append((s, e, row_html[s:e]))
        p = e
    return tds

def get_td_inner(td_html):
    """<td ...>INNER</td> 에서 INNER 반환"""
    end_open = td_html.index('>') + 1
    start_close = td_html.rindex('</td>')
    return td_html[end_open:start_close]

def replace_td_inner(td_html, new_inner):
    """td의 내용만 교체, 속성 유지"""
    end_open = td_html.index('>') + 1
    start_close = td_html.rindex('</td>')
    return td_html[:end_open] + new_inner + td_html[start_close:]

print("페이지 불러오는 중...")
data2 = fetch_page(page_id_week2)
data3 = fetch_page(page_id_week3)

html2 = data2['body']['storage']['value']
html3 = data3['body']['storage']['value']
version3 = data3['version']['number']
title3 = data3['title']

print(f"2주차 버전: {data2['version']['number']}")
print(f"3주차 버전: {version3}, 제목: {title3}")

# ==== 2주차 서다솔 섹션에서 차주계획 td inner 추출 ====
idx2 = html2.find('서다솔')
tr2_start = html2.rfind('<tr', 0, idx2)
pos = tr2_start
rows2_html = []
for i in range(7):
    end = html2.find('</tr>', pos) + 5
    rows2_html.append(html2[pos:end])
    pos = end

# 2주차 차주계획: 각 row의 마지막 td inner
next_week_contents = []
for r in rows2_html:
    tds = split_tds(r)
    last_inner = get_td_inner(tds[-1][2]) if tds else ''
    next_week_contents.append(last_inner)

print("\n=== 2주차 차주계획 내용 ===")
for i, c in enumerate(next_week_contents):
    text = re.sub('<[^>]+>', '', c).strip()[:80]
    print(f"  row[{i}]: {text!r}")

# ==== 3주차 서다솔 섹션 위치 찾기 ====
idx3 = html3.find('서다솔')
tr3_start = html3.rfind('<tr', 0, idx3)
pos = tr3_start
rows3_info = []  # (abs_start, abs_end, row_html)
for i in range(7):
    end = html3.find('</tr>', pos) + 5
    rows3_info.append((pos, end, html3[pos:end]))
    pos = end

print(f"\n3주차 서다솔 섹션: {rows3_info[0][0]} ~ {rows3_info[-1][1]}")

# ==== 3주차 HTML 수정 ====
# 행 구조:
# row[0]: td[0]=서다솔, td[1]=매장업무, td[2]=금주실적, td[3]=진행률, td[4]=차주계획
# row[1]~row[4]: td[0]=금주실적, td[1]=진행률, td[2]=차주계획
# row[5]: td[0]=기타업무, td[1]=금주실적, td[2]=진행률, td[3]=차주계획
# row[6]: td[0]=금주실적, td[1]=진행률, td[2]=차주계획

# 이번 주 추가 실적 HTML (row[0] 첫 번째 금주실적에 포함)
extra_content_row0 = '''<p>[현대목동점 계약 서류]</p><ul>
<li><p>위탁판매 대리점 계약정서 작성 (05.21, 일부 오류 05.22 수정 예정)</p></li>
<li><p>재산종합보험 서류 등록 완료</p></li>
<li><p>임직원 할인 홍보 시안 제작 완료</p></li>
</ul>'''

extra_content_row4 = '''<p>롯데바이오로직스 임직원 공동구매 합의서 작성</p>'''

# 각 row 수정
new_rows = []

for i, (abs_s, abs_e, row_html) in enumerate(rows3_info):
    tds = split_tds(row_html)

    if i == 0:
        # td[2] = 금주실적 → 2주차 row[0] 차주계획 내용 + 추가 실적
        # td[3] = 진행률 → 100%
        # td[4] = 차주계획 → 비움
        new_inner_current = next_week_contents[0] + extra_content_row0
        new_td2 = replace_td_inner(tds[2][2], new_inner_current)
        new_td3 = replace_td_inner(tds[3][2], '<p>100%</p>')
        new_td4 = replace_td_inner(tds[4][2], '<p />')

        new_row = row_html[:tds[2][0]] + new_td2 + new_td3 + new_td4 + '</tr>'
        new_rows.append(new_row)

    elif i in [1, 2, 3]:
        # td[0] = 금주실적 → 2주차 row[i] 차주계획 내용
        # td[1] = 진행률 → 100% (내용 있는 경우)
        # td[2] = 차주계획 → 비움
        src_content = next_week_contents[i]
        has_content = bool(re.sub('<[^>]+>', '', src_content).strip())

        new_td0 = replace_td_inner(tds[0][2], src_content)
        new_td1 = replace_td_inner(tds[1][2], '<p>100%</p>' if has_content else '<p />')
        new_td2 = replace_td_inner(tds[2][2], '<p />')

        new_row = row_html[:tds[0][0]] + new_td0 + new_td1 + new_td2 + '</tr>'
        new_rows.append(new_row)

    elif i == 4:
        # td[0] = 금주실적 → 롯데바이오로직스 추가
        new_td0 = replace_td_inner(tds[0][2], extra_content_row4)
        new_td1 = replace_td_inner(tds[1][2], '<p>100%</p>')
        new_td2 = replace_td_inner(tds[2][2], '<p />')

        new_row = row_html[:tds[0][0]] + new_td0 + new_td1 + new_td2 + '</tr>'
        new_rows.append(new_row)

    elif i == 5:
        # 기타업무 행: td[0]=기타업무, td[1]=금주실적, td[2]=진행률, td[3]=차주계획
        new_td1 = replace_td_inner(tds[1][2], '<p />')
        new_td2 = replace_td_inner(tds[2][2], '<p />')
        new_td3 = replace_td_inner(tds[3][2], '<p />')

        new_row = row_html[:tds[1][0]] + new_td1 + new_td2 + new_td3 + '</tr>'
        new_rows.append(new_row)

    else:
        # row[6]: 그대로
        new_rows.append(row_html)

# 전체 HTML에서 서다솔 섹션 교체
section_start = rows3_info[0][0]
section_end = rows3_info[-1][1]
new_section = ''.join(new_rows)

new_html3 = html3[:section_start] + new_section + html3[section_end:]
print(f"\nHTML 수정 완료 (기존 {len(html3)} → 새 {len(new_html3)} 글자)")

# ==== Confluence PUT 업데이트 ====
payload = json.dumps({
    'version': {'number': version3 + 1},
    'title': title3,
    'type': 'page',
    'body': {
        'storage': {
            'value': new_html3,
            'representation': 'storage'
        }
    }
}, ensure_ascii=False).encode('utf-8')

put_req = urllib.request.Request(
    f'{url_base}/wiki/rest/api/content/{page_id_week3}',
    data=payload,
    headers=headers,
    method='PUT'
)

try:
    with urllib.request.urlopen(put_req) as resp:
        result = json.loads(resp.read())
        new_ver = result['version']['number']
        link = result['_links']['webui']
        print(f"\n✅ 업데이트 성공! 버전 {version3} → {new_ver}")
        print(f"링크: {url_base}/wiki{link}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f"❌ 오류 {e.code}: {e.reason}")
    print(body[:800])
