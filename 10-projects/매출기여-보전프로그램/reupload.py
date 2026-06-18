import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3, requests, json

conn = sqlite3.connect("sales_contribution.db")
conn.execute("DELETE FROM matches")
conn.execute("DELETE FROM erp_orders")
conn.commit()
conn.close()
print("초기화 완료")

for path, label in [
    (r"C:\Users\FURSYS\Downloads\네이버 쿠시노 10주년 라이브.xlsx", "쿠시노"),
    (r"C:\Users\FURSYS\Downloads\네이버 퍼시스 패밀리 페스타 라이브.xlsx", "퍼시스"),
]:
    print(f"\n업로드: {label}")
    with open(path, "rb") as f:
        r = requests.post("http://localhost:8000/api/erp/upload",
            files={"file": (label+".xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    d = r.json()
    print(f"  처리: {d['inserted']}건 | 보전후보: {d['cancel_summary']['보전대상_오프라인_취소']}건 | 매칭: {d['matching']['신규_매칭건수']}건")
    for ev in d['matching']['행사별_현황']:
        print(f"    [{ev['행사명'][:25]}] {ev['매칭건수']}건")
