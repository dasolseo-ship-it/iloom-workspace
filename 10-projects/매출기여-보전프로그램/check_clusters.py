import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

conn = sqlite3.connect("sales_contribution.db")
conn.row_factory = sqlite3.Row

# 클러스터 = (오프라인 고객명 + 동주소 + 이벤트) 기준 중복 제거
total = conn.execute("""
    SELECT COUNT(DISTINCT of.customer_name || '|' || of.address_dong || '|' || m.event_id)
    FROM matches m
    JOIN erp_orders of ON m.offline_order_no = of.order_no
""").fetchone()[0]
print(f"총 클러스터(인별): {total}명")

cancel = conn.execute("""
    SELECT COUNT(DISTINCT of.customer_name || '|' || of.address_dong || '|' || m.event_id)
    FROM matches m
    JOIN erp_orders of ON m.offline_order_no = of.order_no
    WHERE m.result_type != 'active_match'
""").fetchone()[0]
print(f"보전후보: {cancel}명")

active = conn.execute("""
    SELECT COUNT(DISTINCT of.customer_name || '|' || of.address_dong || '|' || m.event_id)
    FROM matches m
    JOIN erp_orders of ON m.offline_order_no = of.order_no
    WHERE m.result_type = 'active_match'
""").fetchone()[0]
print(f"모니터링: {active}명")

print()
print("=== 오프라인 대리점 목록 (상위 20) ===")
rows = conn.execute("SELECT store_name, COUNT(*) as cnt FROM erp_orders WHERE store_type='offline' GROUP BY store_name ORDER BY cnt DESC LIMIT 20").fetchall()
for r in rows:
    print(f"  {r['store_name']}: {r['cnt']}건")

print()
print("=== 온라인 대리점 목록 (전체) ===")
rows = conn.execute("SELECT store_name, COUNT(*) as cnt FROM erp_orders WHERE store_type='online' GROUP BY store_name ORDER BY cnt DESC").fetchall()
for r in rows:
    print(f"  {r['store_name']}: {r['cnt']}건")
