import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect("sales_contribution.db")
conn.row_factory = sqlite3.Row

events = conn.execute("SELECT * FROM events ORDER BY announcement_date").fetchall()
for ev in events:
    lookback = ev["offline_lookback_days"] or 7
    ann = date.fromisoformat(ev["announcement_date"])
    offline_from = (ann - timedelta(days=lookback)).isoformat()
    offline_to = ev["announcement_date"]

    print(f"\n=== {ev['event_name']} ===")
    print(f"  공지일: {ev['announcement_date']}, 소급기간: {lookback}일")
    print(f"  오프라인 수주 범위: {offline_from} ~ {offline_to} (전날까지)")

    # 오프라인 수주 건수
    offline_cnt = conn.execute(
        "SELECT COUNT(*) FROM erp_orders WHERE store_type='offline' AND order_date >= ? AND order_date < ?",
        (offline_from, offline_to)
    ).fetchone()[0]
    print(f"  DB 오프라인 건수(범위내): {offline_cnt}건")

    # 매칭된 오프라인 날짜 분포
    rows = conn.execute("""
        SELECT of.order_date, COUNT(*) as cnt
        FROM matches m
        JOIN erp_orders of ON m.offline_order_no = of.order_no
        WHERE m.event_id = ?
        GROUP BY of.order_date
        ORDER BY of.order_date
    """, (ev["id"],)).fetchall()
    print(f"  매칭된 오프라인 수주 날짜:")
    for r in rows:
        print(f"    {r['order_date']}: {r['cnt']}건")
