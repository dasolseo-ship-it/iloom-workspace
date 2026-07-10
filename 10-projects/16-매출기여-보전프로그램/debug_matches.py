import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

conn = sqlite3.connect("sales_contribution.db")
conn.row_factory = sqlite3.Row

print("=== 쿠시노(id=2) 오프라인 날짜 분포 ===")
rows = conn.execute("""
    SELECT of.order_date, of.order_status, of.cancel_type, COUNT(*) as cnt
    FROM matches m
    JOIN erp_orders of ON m.offline_order_no = of.order_no
    WHERE m.event_id = 2
    GROUP BY of.order_date, of.order_status, of.cancel_type
    ORDER BY of.order_date
""").fetchall()
for r in rows:
    print(f"  {r['order_date']} status={r['order_status']} cancel={r['cancel_type']} cnt={r['cnt']}")

print()
print("=== 퍼시스(id=3) 오프라인 날짜 분포 ===")
rows = conn.execute("""
    SELECT of.order_date, of.order_status, of.cancel_type, COUNT(*) as cnt
    FROM matches m
    JOIN erp_orders of ON m.offline_order_no = of.order_no
    WHERE m.event_id = 3
    GROUP BY of.order_date, of.order_status, of.cancel_type
    ORDER BY of.order_date
""").fetchall()
for r in rows:
    print(f"  {r['order_date']} status={r['order_status']} cancel={r['cancel_type']} cnt={r['cnt']}")

# 필터 테스트
print()
print("=== 직접 필터 테스트 (쿠시노: 2026-04-29 ~ 2026-05-06) ===")
cnt = conn.execute("""
    SELECT COUNT(*) FROM erp_orders
    WHERE store_type = 'offline'
    AND order_date >= '2026-04-29'
    AND order_date < '2026-05-06'
""").fetchone()[0]
print(f"  필터 내 오프라인 건수: {cnt}")

print()
print("=== 쿠시노 온라인 수주 (event_id=2) 건수 ===")
row = conn.execute("SELECT COUNT(*) FROM erp_orders WHERE store_type='online' AND store_name='네이버' AND order_date >= '2026-05-15' AND order_date <= '2026-05-24'").fetchone()
print(f"  네이버 온라인 수주(5/15~5/24): {row[0]}건")
