import requests
import json
import os

TOKEN = os.environ.get("ATLASSIAN_API_TOKEN", "")
EMAIL = os.environ.get("ATLASSIAN_EMAIL", "dasol_seo@fursys.com")
PAGE_ID = "3282924876"
URL = f"https://fursys.atlassian.net/wiki/rest/api/content/{PAGE_ID}"

with open(r"C:\Users\FURSYS\Downloads\iloom-workspace-claude\00-inbox\page_final.html", encoding="utf-8") as f:
    html_content = f.read()

# 현재 버전 확인
r = requests.get(URL, params={"expand": "version"}, auth=(EMAIL, TOKEN))
current_version = r.json()["version"]["number"]
print(f"현재 버전: {current_version}")

payload = {
    "version": {"number": current_version + 1},
    "title": "2026년 6월 2주차(6/8~6/12)",
    "type": "page",
    "body": {
        "storage": {
            "value": html_content,
            "representation": "storage"
        }
    }
}

resp = requests.put(
    URL,
    json=payload,
    auth=(EMAIL, TOKEN),
    headers={"Content-Type": "application/json"}
)

if resp.status_code == 200:
    print(f"성공! 버전: {resp.json()['version']['number']}")
else:
    print(f"오류 {resp.status_code}: {resp.text[:500]}")
