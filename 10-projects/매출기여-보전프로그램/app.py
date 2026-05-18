"""
매출기여 보전 프로그램
온라인 행사로 인한 오프라인 수주 취소건 보전금 관리
"""
import sqlite3
import io
from datetime import date, timedelta
from typing import List, Optional
from contextlib import contextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="매출기여 보전 프로그램")
templates = Jinja2Templates(directory="templates")

DB_PATH = "sales_contribution.db"

# ================================================================
# 일룸 시리즈 / 품목 설정
# ================================================================
SERIES_LIST = sorted([
    "쿠시노코지", "쿠시노",
    "로이모노", "로이",
    "에디키즈", "에디",
    "바젤SS", "바젤", "반트SS", "반트",
    "멘디", "클러치", "포레스트", "렉스",
    "퍼스트", "파로", "라비", "워드",
    "스탠다", "학생방", "기타",
], key=len, reverse=True)  # 긴 이름 우선 매칭

CATEGORIES = [
    "침대", "소파", "책상", "의자", "수납장", "옷장",
    "서랍장", "화장대", "거울", "선반", "책장", "식탁",
    "파티션", "기타",
]

# 쿠시노 ≠ 쿠시노코지, 로이 ≠ 로이모노
EXCLUSION_RULES: dict[str, list[str]] = {
    "쿠시노": ["쿠시노코지"],
    "쿠시노코지": ["쿠시노"],
    "로이": ["로이모노"],
    "로이모노": ["로이"],
}


# ================================================================
# DB
# ================================================================
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                announcement_date TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS event_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                product_name TEXT NOT NULL,
                series TEXT NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT NOT NULL,
                order_date TEXT NOT NULL,
                customer_amount REAL NOT NULL,
                event_id INTEGER REFERENCES events(id),
                result_type TEXT,
                compensation REAL DEFAULT 0,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS order_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_name TEXT NOT NULL,
                series TEXT NOT NULL,
                category TEXT NOT NULL,
                match_status TEXT DEFAULT 'pending'
            );
        """)


init_db()


# ================================================================
# 매칭 로직
# ================================================================
def is_same_series(s1: str, s2: str) -> bool:
    s1, s2 = s1.strip(), s2.strip()
    if s1 == s2:
        return True
    # 예외 규칙 적용
    if s2 in EXCLUSION_RULES.get(s1, []):
        return False
    return False


def match_products(order_products: list[dict], event_products: list[dict]) -> list[dict]:
    """수주 상품별 인정 여부 판정"""
    results = []
    for op in order_products:
        matched = any(
            is_same_series(op["series"], ep["series"]) and op["category"] == ep["category"]
            for ep in event_products
        )
        results.append({**op, "match_status": "approved" if matched else "rejected"})
    return results


def calc_result(matched: list[dict], customer_amount: float) -> tuple[str, float, str]:
    """(result_type, compensation, note) 반환"""
    approved = [p for p in matched if p["match_status"] == "approved"]
    rejected = [p for p in matched if p["match_status"] == "rejected"]

    if not approved:
        return "rejected", 0.0, ""
    if not rejected:
        return "full", round(customer_amount * 0.05, 0), ""
    # 부분인정: 결제액 분리 기준이 정책에 없으므로 전체 5% 지급 후 별도 조정 안내
    note = f"부분인정 ({len(approved)}/{len(matched)}개 상품). 결제액 배분 기준 별도 확인 필요."
    return "partial", round(customer_amount * 0.05, 0), note


# ================================================================
# Pydantic Models
# ================================================================
class ProductIn(BaseModel):
    product_name: str
    series: str
    category: str


class EventIn(BaseModel):
    event_name: str
    announcement_date: str
    start_date: str
    end_date: str
    products: List[ProductIn]


class OrderIn(BaseModel):
    store_name: str
    order_date: str
    customer_amount: float
    event_id: int
    products: List[ProductIn]


# ================================================================
# Routes
# ================================================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/config")
async def get_config():
    return {"series": SERIES_LIST, "categories": CATEGORIES}


# --- 행사 ---
@app.post("/api/events")
async def create_event(event: EventIn):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO events (event_name, announcement_date, start_date, end_date) VALUES (?,?,?,?)",
            (event.event_name, event.announcement_date, event.start_date, event.end_date),
        )
        event_id = cur.lastrowid
        for p in event.products:
            conn.execute(
                "INSERT INTO event_products (event_id, product_name, series, category) VALUES (?,?,?,?)",
                (event_id, p.product_name, p.series, p.category),
            )
    return {"id": event_id, "message": "행사 등록 완료"}


@app.get("/api/events")
async def list_events():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY announcement_date DESC").fetchall()
        result = []
        for e in rows:
            products = conn.execute(
                "SELECT * FROM event_products WHERE event_id=?", (e["id"],)
            ).fetchall()
            result.append({**dict(e), "products": [dict(p) for p in products]})
    return result


@app.delete("/api/events/{event_id}")
async def delete_event(event_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    return {"message": "삭제 완료"}


# 커넥트플러스 Excel 업로드
@app.post("/api/events/upload")
async def upload_events(file: UploadFile = File(...)):
    import openpyxl
    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content))
    ws = wb.active

    # 헤더: 행사명 | 공지일 | 시작일 | 종료일 | 상품명 | 시리즈 | 품목
    headers = [str(c.value).strip() if c.value else "" for c in ws[1]]
    required = {"행사명", "공지일", "시작일", "종료일", "상품명", "시리즈", "품목"}
    if not required.issubset(set(headers)):
        raise HTTPException(400, f"Excel 헤더 오류. 필요: {required}, 실제: {set(headers)}")

    idx = {h: headers.index(h) for h in required}
    events_map: dict[str, dict] = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[idx["행사명"]]:
            continue
        name = str(row[idx["행사명"]]).strip()
        if name not in events_map:
            events_map[name] = {
                "event_name": name,
                "announcement_date": str(row[idx["공지일"]])[:10],
                "start_date": str(row[idx["시작일"]])[:10],
                "end_date": str(row[idx["종료일"]])[:10],
                "products": [],
            }
        events_map[name]["products"].append(
            ProductIn(
                product_name=str(row[idx["상품명"]]).strip(),
                series=str(row[idx["시리즈"]]).strip(),
                category=str(row[idx["품목"]]).strip(),
            )
        )

    created = []
    for ev in events_map.values():
        res = await create_event(EventIn(**ev))
        created.append(res["id"])

    return {"message": f"{len(created)}개 행사 등록 완료", "event_ids": created}


# --- 수주 ---
@app.post("/api/orders")
async def create_order(order: OrderIn):
    with get_db() as conn:
        event = conn.execute("SELECT * FROM events WHERE id=?", (order.event_id,)).fetchone()
        if not event:
            raise HTTPException(404, "행사를 찾을 수 없습니다")

        # D-1 체크
        od = date.fromisoformat(order.order_date)
        ad = date.fromisoformat(event["announcement_date"])
        if od > ad - timedelta(days=1):
            raise HTTPException(
                400,
                f"수주일({order.order_date})이 행사 공지 D-1({ad - timedelta(days=1)}) 이후입니다. 매출기여 대상 외."
            )

        event_products = [
            dict(p) for p in conn.execute(
                "SELECT * FROM event_products WHERE event_id=?", (order.event_id,)
            ).fetchall()
        ]

        matched = match_products([p.model_dump() for p in order.products], event_products)
        result_type, compensation, note = calc_result(matched, order.customer_amount)

        cur = conn.execute(
            "INSERT INTO orders (store_name, order_date, customer_amount, event_id, result_type, compensation, note) VALUES (?,?,?,?,?,?,?)",
            (order.store_name, order.order_date, order.customer_amount,
             order.event_id, result_type, compensation, note),
        )
        order_id = cur.lastrowid

        for p in matched:
            conn.execute(
                "INSERT INTO order_products (order_id, product_name, series, category, match_status) VALUES (?,?,?,?,?)",
                (order_id, p["product_name"], p["series"], p["category"], p["match_status"]),
            )

    label = {"full": "✅ 전체 인정", "partial": "⚠️ 부분 인정", "rejected": "❌ 불인정"}
    return {
        "id": order_id,
        "result_type": result_type,
        "compensation": compensation,
        "products": matched,
        "note": note,
        "message": label[result_type],
    }


@app.get("/api/orders")
async def list_orders():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT o.*, e.event_name
            FROM orders o
            LEFT JOIN events e ON o.event_id = e.id
            ORDER BY o.created_at DESC
        """).fetchall()
        result = []
        for o in rows:
            products = conn.execute(
                "SELECT * FROM order_products WHERE order_id=?", (o["id"],)
            ).fetchall()
            result.append({**dict(o), "products": [dict(p) for p in products]})
    return result


@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    return {"message": "삭제 완료"}


@app.get("/api/stats")
async def get_stats():
    with get_db() as conn:
        s = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN result_type='full' THEN 1 ELSE 0 END) as full_cnt,
                SUM(CASE WHEN result_type='partial' THEN 1 ELSE 0 END) as partial_cnt,
                SUM(CASE WHEN result_type='rejected' THEN 1 ELSE 0 END) as rejected_cnt,
                SUM(COALESCE(compensation, 0)) as total_compensation
            FROM orders
        """).fetchone()
    return dict(s)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
