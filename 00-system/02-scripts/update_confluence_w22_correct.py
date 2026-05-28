# -*- coding: utf-8 -*-
"""
Confluence W22 업데이트 - 올바른 페이지
스페이스: R7hIqkF4w0UZ / 페이지 ID: 3155297715
컬럼: 담당자 | 구분 | 금주 업무 실적 | 진행률(%) | 차주 업무 계획
"""
import urllib.request, base64, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')
page_id = '3155297715'

creds = base64.b64encode(f'{email}:{token}'.encode()).decode()
headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}

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

# ── 매장 업무 TR[0] 교체 ──────────────────────────────────────────────────
old_tr0 = '<tr ac:local-id="581a6e0b-3160-43aa-a228-7674f04656f4"><td rowspan="7" ac:local-id="c8e53f2c-1bb5-4351-86f7-1beda369d0bd"><p local-id="14206080-b56f-42ad-9fcc-581d5b438e1d" style="text-align: center;">서다솔</p></td><td rowspan="5" ac:local-id="015fcbbc-0bc7-4527-9755-bba8f9438740"><p local-id="564285e4-b045-4a2c-a060-61bc9fea4fe6" style="text-align: center;">매장 업무</p></td><td ac:local-id="3596dc9e-aa99-4249-831c-262080084d59"><p local-id="401b8f4b-c8f9-4d15-b588-9ef05c9d0a6b" /></td><td ac:local-id="b357bc68-7146-4f4f-88a5-7a3515a556fd"><p local-id="3fc216c0-75a9-4cea-b858-593eb5478f51" /></td><td ac:local-id="46474ff2-67fb-40d6-8ea5-27a64d0f6c81"><p local-id="c2bc5e7f-0923-4f6c-b8ed-6a61f64616a4" /></td></tr>'

new_tr0 = '''<tr ac:local-id="581a6e0b-3160-43aa-a228-7674f04656f4"><td rowspan="7" ac:local-id="c8e53f2c-1bb5-4351-86f7-1beda369d0bd"><p local-id="14206080-b56f-42ad-9fcc-581d5b438e1d" style="text-align: center;">서다솔</p></td><td rowspan="5" ac:local-id="015fcbbc-0bc7-4527-9755-bba8f9438740"><p local-id="564285e4-b045-4a2c-a060-61bc9fea4fe6" style="text-align: center;">매장 업무</p></td><td ac:local-id="3596dc9e-aa99-4249-831c-262080084d59"><p>롯데영등포점</p><ul><li><p>구세군작업장 B2B 협조전 작성 (21% 할인공급요청서 포함)</p></li></ul><p>롯데인천2점</p><ul><li><p>팝업 계약연장 품의서 및 계약정서 작성 (~2026.07.31)</p></li></ul><p>현대목동점</p><ul><li><p>인테리어 설치 합의서 공사범위별 금액 회신 (총 88,658,000원 / VAT 별도)</p></li></ul></td><td ac:local-id="b357bc68-7146-4f4f-88a5-7a3515a556fd"><p /></td><td ac:local-id="46474ff2-67fb-40d6-8ea5-27a64d0f6c81"><ul><li><p>담당 매장 순방</p></li><li><p>롯데인천2점 계약연장 서류 최종 확인</p></li></ul></td></tr>'''

# ── 기타 업무 TR[5] 교체 ──────────────────────────────────────────────────
old_tr5 = '<tr ac:local-id="8c3c0fdb-80dd-4d6e-8052-9e7e860fc5af"><td rowspan="2" ac:local-id="d7be7985-66bf-46ef-b0d9-c2f16ce2f74f"><p local-id="37832a6d-5251-4492-9be1-5f412aeb592d" style="text-align: center;">기타 업무</p></td><td ac:local-id="c5ab4ae9-1931-4cba-8dc1-fcb3192929af"><p local-id="22a80e56-148f-4b83-9305-afb8ca84ab76" /></td><td ac:local-id="8764a136-95ce-4d72-9a18-bb2d3903ae2d"><p local-id="e537'

# TR[5] 전체를 찾아서 교체
idx_tr5 = html.find('8c3c0fdb-80dd-4d6e-8052-9e7e860fc5af')
tr5_start = html.rfind('<tr', 0, idx_tr5)
tr5_end = html.find('</tr>', idx_tr5) + 5
old_tr5_full = html[tr5_start:tr5_end]

new_tr5 = '''<tr ac:local-id="8c3c0fdb-80dd-4d6e-8052-9e7e860fc5af"><td rowspan="2" ac:local-id="d7be7985-66bf-46ef-b0d9-c2f16ce2f74f"><p local-id="37832a6d-5251-4492-9be1-5f412aeb592d" style="text-align: center;">기타 업무</p></td><td ac:local-id="c5ab4ae9-1931-4cba-8dc1-fcb3192929af"><ul><li><p>6월 비용 예측 / 5월 비용 채산 리뷰</p></li><li><p>온오프 보전 시스템 — 엑셀 내보내기 API 개발 (GET /api/orders/export)</p></li><li><p>온오프 보전 시스템 — 매장별 집계 API 개발 (GET /api/stats/by-store)</p></li><li><p>데이터 매칭 아키텍처 탐색 (ERP export 분석, 매칭 키 확정: 이름+주소+휴대폰 뒷 4자리)</p></li></ul></td><td ac:local-id="8764a136-95ce-4d72-9a18-bb2d3903ae2d"><p /></td><td ac:local-id="''' + old_tr5_full.split('ac:local-id="')[-1].split('"')[0] + '''"><ul><li><p>선우님 확인: 휴대폰 뒷 4자리 출처 및 bulk export 가능 여부</p></li><li><p>온오프 보전 시스템 — 데이터 파이프라인 설계 착수</p></li></ul></td></tr>'''

# HTML 교체
if old_tr0 not in html:
    print("❌ TR[0] 매칭 실패")
    sys.exit(1)

new_html = html.replace(old_tr0, new_tr0, 1)
new_html = new_html.replace(old_tr5_full, new_tr5, 1)
print(f"HTML 수정 완료 ({len(html)} → {len(new_html)} 글자)")

# Confluence 업데이트
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
    print(body[:800])
