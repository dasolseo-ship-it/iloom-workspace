import sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
c = sqlite3.connect('sales_contribution.db')
c.row_factory = sqlite3.Row

print("=== 5월 전체 오프라인 수주 날짜별 건수 ===")
rows = c.execute("""
    SELECT order_date, COUNT(*) as cnt
    FROM erp_orders
    WHERE store_type = 'offline'
    AND order_date >= '2026-05-01'
    AND order_date < '2026-06-01'
    GROUP BY order_date ORDER BY order_date
""").fetchall()
for r in rows:
    print(str(r['order_date']) + ': ' + str(r['cnt']) + '건')
