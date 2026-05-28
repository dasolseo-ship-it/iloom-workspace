# -*- coding: utf-8 -*-
import urllib.request, base64, json, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')
page_id = '906311582'

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
print(f"버전: {version}")

# 경기/서울 담당 서다솔 행 찾기
keywords = ['현대목동', '롯데영등포', '롯데인천', '롯데구리', '수도권']
for kw in keywords:
    idx = html.find(kw)
    if idx >= 0:
        tr_start = html.rfind('<tr', 0, idx)
        tr_end = html.find('</tr>', idx) + 5
        row = html[tr_start:tr_end]
        print(f"\n=== '{kw}' 발견 (위치 {idx}) ===")
        print(row[:600])
        break

# 모든 행 담당자 이름 파싱
print("\n\n=== 전체 담당자 목록 ===")
# numberingColumn 있는 TR들 찾기
trs = re.findall(r'<tr>.*?</tr>', html, re.DOTALL)
numbered_trs = [tr for tr in trs if 'numberingColumn' in tr]
for tr in numbered_trs:
    # 지역
    region = re.search(r'text-align: center;">(.*?)</p>', tr)
    # 담당자 이름 (3번째 td쯤)
    manager = re.findall(r'<p[^>]*>([가-힣]{2,4})</p>', tr)
    row_num = re.search(r'numberingColumn">(\d+)', tr)
    if region:
        print(f"행{row_num.group(1) if row_num else '?'}: {region.group(1)} | 이름: {manager[:3]}")
