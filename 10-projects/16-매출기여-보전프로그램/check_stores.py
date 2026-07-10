import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

conn = sqlite3.connect("sales_contribution.db")
conn.row_factory = sqlite3.Row

print("=== 현재 오프라인으로 분류된 대리점 전체 목록 ===")
rows = conn.execute("""
    SELECT store_name, COUNT(*) as cnt
    FROM erp_orders
    WHERE store_type = 'offline'
    GROUP BY store_name
    ORDER BY cnt DESC
""").fetchall()
for r in rows:
    print(f"  {r['store_name']}: {r['cnt']}건")

print("\n=== 현재 온라인으로 분류된 대리점 전체 목록 ===")
rows = conn.execute("""
    SELECT store_name, COUNT(*) as cnt
    FROM erp_orders
    WHERE store_type = 'online'
    GROUP BY store_name
    ORDER BY cnt DESC
""").fetchall()
for r in rows:
    print(f"  {r['store_name']}: {r['cnt']}건")

conn.close()
