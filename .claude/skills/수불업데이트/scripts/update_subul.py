#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, json, argparse
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1D5Ut0a-Y3gT-vJCQXOEy5j_qgeCE8v_uM-bVMma0x14"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(_DIR, "..", "..", "..", "..", "00-system", "02-scripts", "service_account.json")
FILTER_DEPT = "리테일사업팀"
DONE_STATUS = "처리완료"


def authenticate():
    return Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)


def find_worksheet(sh):
    for ws in sh.worksheets():
        try:
            headers = ws.row_values(1)
            if "수주번호" in headers and "처리결과" in headers:
                return ws
        except Exception:
            continue
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--numbers", required=True)
    parser.add_argument("--person", default="채선경")
    args = parser.parse_args()
    FILTER_PERSON = args.person
    erp_set = {n.strip().upper() for n in args.numbers.split(",") if n.strip()}

    try:
        gc = gspread.authorize(authenticate())
        sh = gc.open_by_key(SHEET_ID)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    ws = find_worksheet(sh)
    if not ws:
        print(json.dumps({"error": "시트 탭을 찾을 수 없습니다"}, ensure_ascii=False))
        sys.exit(1)

    all_values = ws.get_all_values()
    headers = all_values[0]
    ci_order  = headers.index("수주번호")
    ci_dept   = headers.index("담당부서")
    ci_person = headers.index("영업담당")
    ci_result = headers.index("처리결과")
    ci_name   = headers.index("수주건명") if "수주건명" in headers else None

    updated, still_open, batch = [], [], []
    for i, row in enumerate(all_values[1:], start=2):
        if len(row) <= max(ci_order, ci_dept, ci_person, ci_result):
            continue
        if row[ci_dept].strip() != FILTER_DEPT or row[ci_person].strip() != FILTER_PERSON:
            continue
        if row[ci_result].strip() == DONE_STATUS:
            continue
        order = row[ci_order].strip()
        name = row[ci_name].strip() if ci_name and len(row) > ci_name else ""
        if order.upper() in erp_set:
            still_open.append({"수주번호": order, "수주건명": name, "현재상태": row[ci_result].strip()})
            continue
        batch.append({
            "range": gspread.utils.rowcol_to_a1(i, ci_result + 1),
            "values": [[DONE_STATUS]]
        })
        updated.append({"수주번호": order, "수주건명": name, "기존처리결과": row[ci_result].strip()})

    if batch:
        ws.batch_update(batch)

    print(json.dumps({
        "updated_count": len(updated),
        "updated": updated,
        "still_open": still_open,
        "worksheet": ws.title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
