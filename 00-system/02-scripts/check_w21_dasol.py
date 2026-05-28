# -*- coding: utf-8 -*-
import urllib.request, base64, json, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

url_base = 'https://fursys.atlassian.net'
email = 'dasol_seo@fursys.com'
token = os.environ.get('CONFLUENCE_TOKEN', '')
page_id = '906210046'  # W21

creds = base64.b64encode(f'{email}:{token}'.encode()).decode()
headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}

req = urllib.request.Request(
    f'{url_base}/wiki/rest/api/content/{page_id}?expand=body.storage,version',
    headers=headers
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

html = data['body']['storage']['value']
print(f"W21 버전: {data['version']['number']}")

# 전체 담당자 목록
trs = re.findall(r'<tr>.*?</tr>', html, re.DOTALL)
numbered_trs = [tr for tr in trs if 'numberingColumn' in tr]
print("\n=== W21 담당자 목록 ===")
for tr in numbered_trs:
    region = re.search(r'text-align: center;">(.*?)</p>', tr)
    managers = re.findall(r'<p[^>]*>([가-힣]{2,4})</p>', tr)
    row_num = re.search(r'numberingColumn">(\d+)', tr)
    if region:
        print(f"행{row_num.group(1) if row_num else '?'}: {region.group(1)} | {managers[:3]}")

# 서다솔 행 내용 전체
print("\n=== W21 서다솔 행 ===")
idx = html.find('서다솔')
tr_start = html.rfind('<tr', 0, idx)
tr_end = html.find('</tr>', idx) + 5
row = html[tr_start:tr_end]
region = re.search(r'text-align: center;">(.*?)</p>', row)
stores = re.findall(r'<td><p>(.*?)</p></td>', row)
print(f"지역: {region.group(1) if region else '없음'}")
print(f"매장: {stores[:2] if stores else '없음'}")
print(f"행 앞 400자:\n{row[:400]}")
