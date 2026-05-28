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

# 모든 서다솔 위치 찾기
positions = []
start = 0
while True:
    idx = html.find('서다솔', start)
    if idx < 0:
        break
    positions.append(idx)
    start = idx + 1

print(f"서다솔 총 {len(positions)}개 발견: {positions}")

# 각 위치의 행(TR) 전체 추출
for i, idx in enumerate(positions):
    tr_start = html.rfind('<tr', 0, idx)
    tr_end = html.find('</tr>', idx) + 5
    row = html[tr_start:tr_end]
    print(f"\n=== 서다솔 행 {i+1} (위치 {idx}) ===")
    # 지역명 추출
    region = re.search(r'text-align: center;">(.*?)</p>', row)
    if region:
        print(f"지역: {region.group(1)}")
    print(f"행 길이: {len(row)}")
    print(row[:300])
