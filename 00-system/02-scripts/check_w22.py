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
print(f"버전: {version}, HTML 길이: {len(html)}")

# 서다솔 찾기
idx = html.find('서다솔')
print(f"서다솔 위치: {idx}")

if idx >= 0:
    print(html[max(0, idx-200):idx+500])
else:
    # 이름 패턴 찾기
    names = re.findall(r'<p[^>]*>([가-힣]{2,4})</p>', html)
    unique_names = list(set(names))
    print(f"발견된 이름 수: {len(unique_names)}")
    print("이름들:", unique_names[:20])

    # HTML 첫 500자 확인
    print("\nHTML 첫 300자:")
    print(repr(html[:300]))
