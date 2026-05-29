"""
매출기여 보전 프로그램
온라인 행사로 인한 오프라인 수주 취소건 보전금 관리
"""
import re
import json
import sqlite3
import io
from datetime import date, timedelta
from typing import List, Optional
from contextlib import contextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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

# 온라인 채널 분류 기준
ONLINE_STORES = frozenset([
    '네이버', '일룸쇼핑몰', '쿠팡', '쿠팡로켓', '엘롯데', 'LG홈스타일',
    'EB', 'AS', '온라인사업부',
])

# 담당 오프라인 매장 (CLAUDE.md 기준)
MY_STORES = frozenset([
    '송도5', '인천검단', '인천중앙2', '김포5', '부천3', '의정부8', '신세계시흥2',
    '현대목동', '롯데구리', '롯데인천2', '롯데영등포',
])

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

            CREATE TABLE IF NOT EXISTS erp_orders (
                order_no TEXT PRIMARY KEY,
                order_base TEXT NOT NULL,
                order_seq INTEGER NOT NULL DEFAULT 0,
                store_name TEXT NOT NULL,
                store_type TEXT NOT NULL,
                order_status TEXT NOT NULL,
                customer_name TEXT DEFAULT '',
                order_date TEXT,
                delivery_date TEXT,
                amount REAL DEFAULT 0,
                address_dong TEXT,
                phone_last4 TEXT,
                cancel_type TEXT,
                import_date TEXT DEFAULT (date('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offline_order_no TEXT NOT NULL,
                online_order_no TEXT NOT NULL,
                event_id INTEGER REFERENCES events(id),
                match_keys TEXT,
                match_confidence TEXT DEFAULT 'medium',
                result_type TEXT,
                compensation REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS match_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
                product_name TEXT DEFAULT '',
                series TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL DEFAULT 0,
                match_status TEXT DEFAULT 'pending'
            );
        """)


init_db()


# ================================================================
# ERP 헬퍼 함수
# ================================================================
def extract_customer_name(order_name: str) -> str:
    """수주건명에서 고객명 추출. 예) (온라인택배)이상이(이*름) → 이상이"""
    if not order_name:
        return ""
    s = re.sub(r'^(\([^)]*\)\s*)+', '', order_name.strip())
    m = re.match(r'^([가-힣]{2,4})(?:\(|$)', s)
    return m.group(1) if m else ""


def parse_order_no(order_no: str) -> tuple[str, int]:
    """I20260529-0088-01 → ('I20260529-0088', 1)"""
    m = re.match(r'^(.*)-(\d+)$', str(order_no).strip())
    if m:
        return m.group(1), int(m.group(2))
    return order_no, 0


def classify_cancel_types(conn):
    """취소건을 date_change / pure_cancel 로 분류"""
    all_rows = conn.execute(
        "SELECT order_no, order_base, order_seq FROM erp_orders"
    ).fetchall()

    base_max: dict[str, int] = {}
    for r in all_rows:
        b = r["order_base"]
        if b not in base_max or r["order_seq"] > base_max[b]:
            base_max[b] = r["order_seq"]

    for r in conn.execute(
        "SELECT order_no, order_base, order_seq FROM erp_orders WHERE order_status='취소'"
    ).fetchall():
        ct = "date_change" if r["order_seq"] < base_max.get(r["order_base"], 0) else "pure_cancel"
        conn.execute("UPDATE erp_orders SET cancel_type=? WHERE order_no=?", (ct, r["order_no"]))


def run_matching_engine(conn) -> int:
    """오프라인 순수취소건 ↔ 온라인 수주건 자동 매칭"""
    events = conn.execute("SELECT * FROM events ORDER BY announcement_date").fetchall()

    offline_cancels = conn.execute("""
        SELECT * FROM erp_orders
        WHERE store_type='offline'
        AND cancel_type='pure_cancel'
        AND customer_name != ''
        AND address_dong IS NOT NULL
    """).fetchall()

    matched = 0
    for oc in offline_cancels:
        for ev in events:
            if (oc["order_date"] or "") >= ev["announcement_date"]:
                continue

            online_orders = conn.execute("""
                SELECT * FROM erp_orders
                WHERE store_type='online'
                AND order_status='수주'
                AND customer_name=?
                AND address_dong=?
                AND order_date >= ?
                AND order_date <= ?
            """, (oc["customer_name"], oc["address_dong"],
                  ev["start_date"], ev["end_date"])).fetchall()

            for oo in online_orders:
                exists = conn.execute(
                    "SELECT 1 FROM matches WHERE offline_order_no=? AND online_order_no=?",
                    (oc["order_no"], oo["order_no"])
                ).fetchone()
                if exists:
                    continue

                keys = ["customer_name", "address_dong"]
                if oc["phone_last4"] and oo["phone_last4"] and oc["phone_last4"] == oo["phone_last4"]:
                    keys.append("phone_last4")

                conn.execute("""
                    INSERT INTO matches
                    (offline_order_no, online_order_no, event_id, match_keys, match_confidence, compensation)
                    VALUES (?,?,?,?,?,?)
                """, (
                    oc["order_no"], oo["order_no"], ev["id"],
                    json.dumps(keys, ensure_ascii=False),
                    "high" if len(keys) >= 3 else "medium",
                    round((oc["amount"] or 0) * 0.05, 0),
                ))
                matched += 1

    return matched


# ================================================================
# 기존 매칭 로직
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


class MatchStatusUpdate(BaseModel):
    status: str


class MatchProductIn(BaseModel):
    product_name: str = ""
    series: str
    category: str
    amount: float = 0


def calc_result_by_product(matched: list[dict]) -> tuple[str, float, str]:
    """품목별 금액 기반 (result_type, compensation, note) 계산"""
    approved = [p for p in matched if p["match_status"] == "approved"]
    rejected = [p for p in matched if p["match_status"] == "rejected"]

    if not approved:
        return "rejected", 0.0, ""

    approved_amount = sum(p.get("amount", 0) for p in approved)
    compensation = round(approved_amount * 0.05, 0)

    if not rejected:
        return "full", compensation, ""

    note = (f"부분인정 ({len(approved)}/{len(matched)}개 상품) "
            f"| 인정 금액 ₩{approved_amount:,.0f}")
    return "partial", compensation, note


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


@app.get("/api/stats/by-store")
async def get_stats_by_store():
    """매장별 집계 통계"""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT
                store_name,
                COUNT(*) as total,
                SUM(CASE WHEN result_type IN ('full','partial') THEN 1 ELSE 0 END) as approved_cnt,
                SUM(CASE WHEN result_type='rejected' THEN 1 ELSE 0 END) as rejected_cnt,
                SUM(COALESCE(compensation, 0)) as total_compensation
            FROM orders
            GROUP BY store_name
            ORDER BY total_compensation DESC
        """).fetchall()
    return [dict(r) for r in rows]


# ================================================================
# 엑셀 내보내기
# ================================================================
@app.get("/api/orders/export")
async def export_orders():
    """보전금 현황 엑셀 다운로드 (전체 수주 목록 + 매장별 집계)"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    BRAND_RED = "C80A1E"
    HEADER_BG = "C80A1E"
    HEADER_FONT = "FFFFFF"
    LIGHT_GRAY = "F5F5F5"
    GREEN_BG = "E8F5E9"
    YELLOW_BG = "FFF9C4"
    RED_BG = "FFEBEE"

    thin = Side(style="thin", color="DDDDDD")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def header_style(cell, bold=True):
        cell.font = Font(name="맑은 고딕", bold=bold, color=HEADER_FONT, size=10)
        cell.fill = PatternFill("solid", fgColor=HEADER_BG)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

    def data_style(cell, bold=False, color=None, align="left"):
        cell.font = Font(name="맑은 고딕", bold=bold, size=9)
        if color:
            cell.fill = PatternFill("solid", fgColor=color)
        cell.alignment = Alignment(horizontal=align, vertical="center")
        cell.border = border

    with get_db() as conn:
        orders = conn.execute("""
            SELECT o.*, e.event_name
            FROM orders o
            LEFT JOIN events e ON o.event_id = e.id
            ORDER BY o.store_name, o.order_date
        """).fetchall()
        store_stats = conn.execute("""
            SELECT
                store_name,
                COUNT(*) as total,
                SUM(CASE WHEN result_type IN ('full','partial') THEN 1 ELSE 0 END) as approved_cnt,
                SUM(CASE WHEN result_type='rejected' THEN 1 ELSE 0 END) as rejected_cnt,
                SUM(COALESCE(compensation, 0)) as total_compensation
            FROM orders
            GROUP BY store_name
            ORDER BY total_compensation DESC
        """).fetchall()

    wb = openpyxl.Workbook()

    # ── 시트 1: 전체 수주 목록 ──
    ws1 = wb.active
    ws1.title = "보전금_수주목록"
    ws1.sheet_view.showGridLines = False
    ws1.freeze_panes = "A2"

    headers1 = ["No", "매장명", "수주일", "행사명", "고객결제액(원)", "보전금(원)", "결과", "비고"]
    col_widths1 = [5, 14, 12, 24, 16, 14, 10, 30]
    ws1.row_dimensions[1].height = 22

    for col, (h, w) in enumerate(zip(headers1, col_widths1), 1):
        cell = ws1.cell(row=1, column=col, value=h)
        header_style(cell)
        ws1.column_dimensions[get_column_letter(col)].width = w

    result_map = {"full": "전체인정", "partial": "부분인정", "rejected": "불인정"}
    result_color = {"full": GREEN_BG, "partial": YELLOW_BG, "rejected": RED_BG}

    for i, o in enumerate(orders, 1):
        row = i + 1
        ws1.row_dimensions[row].height = 18
        rt = o["result_type"] or ""
        row_color = result_color.get(rt, None)

        values = [
            i,
            o["store_name"],
            o["order_date"],
            o["event_name"] or "-",
            o["customer_amount"],
            o["compensation"] or 0,
            result_map.get(rt, "-"),
            o["note"] or "",
        ]
        for col, val in enumerate(values, 1):
            cell = ws1.cell(row=row, column=col, value=val)
            is_amount = col in (5, 6)
            data_style(cell, align="right" if is_amount else ("center" if col in (1, 3, 7) else "left"),
                       color=row_color if not is_amount else None)
            if is_amount:
                cell.number_format = '#,##0'
                if row_color:
                    cell.fill = PatternFill("solid", fgColor=row_color)

    # 합계 행
    total_row = len(orders) + 2
    ws1.row_dimensions[total_row].height = 20
    ws1.cell(total_row, 1, "합계").font = Font(name="맑은 고딕", bold=True, size=10)
    ws1.cell(total_row, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws1.cell(total_row, 1).fill = PatternFill("solid", fgColor="F0F0F0")
    ws1.cell(total_row, 1).border = border

    total_amount = sum(o["customer_amount"] for o in orders)
    total_comp = sum((o["compensation"] or 0) for o in orders)
    for col in range(2, 9):
        cell = ws1.cell(total_row, col)
        if col == 5:
            cell.value = total_amount
            cell.number_format = '#,##0'
            cell.font = Font(name="맑은 고딕", bold=True, size=10)
        elif col == 6:
            cell.value = total_comp
            cell.number_format = '#,##0'
            cell.font = Font(name="맑은 고딕", bold=True, color=BRAND_RED, size=10)
        cell.fill = PatternFill("solid", fgColor="F0F0F0")
        cell.alignment = Alignment(horizontal="right" if col in (5, 6) else "center", vertical="center")
        cell.border = border

    # ── 시트 2: 매장별 집계 ──
    ws2 = wb.create_sheet("매장별집계")
    ws2.sheet_view.showGridLines = False

    # 타이틀
    ws2.merge_cells("A1:E1")
    title_cell = ws2["A1"]
    title_cell.value = "일룸 매출기여 보전 프로그램 — 매장별 집계"
    title_cell.font = Font(name="맑은 고딕", bold=True, size=13, color=BRAND_RED)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 28

    # 부제목
    ws2.merge_cells("A2:E2")
    sub_cell = ws2["A2"]
    sub_cell.value = f"출력일: {date.today().strftime('%Y-%m-%d')}  |  적용기간: 2026.05.01 ~ 2027.05.31"
    sub_cell.font = Font(name="맑은 고딕", size=9, color="888888")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[2].height = 16

    headers2 = ["매장명", "전체건수", "인정건수", "불인정건수", "보전금합계(원)"]
    col_widths2 = [16, 12, 12, 12, 18]
    ws2.row_dimensions[3].height = 22

    for col, (h, w) in enumerate(zip(headers2, col_widths2), 1):
        cell = ws2.cell(row=3, column=col, value=h)
        header_style(cell)
        ws2.column_dimensions[get_column_letter(col)].width = w

    for i, s in enumerate(store_stats, 1):
        row = i + 3
        ws2.row_dimensions[row].height = 18
        bg = LIGHT_GRAY if i % 2 == 0 else "FFFFFF"
        vals = [s["store_name"], s["total"], s["approved_cnt"], s["rejected_cnt"], s["total_compensation"]]
        for col, val in enumerate(vals, 1):
            cell = ws2.cell(row=row, column=col, value=val)
            is_amount = col == 5
            data_style(cell, align="right" if is_amount else ("center" if col > 1 else "left"), color=bg)
            if is_amount:
                cell.number_format = '#,##0'
                if s["total_compensation"] > 0:
                    cell.font = Font(name="맑은 고딕", bold=True, color=BRAND_RED, size=9)
                cell.fill = PatternFill("solid", fgColor=bg)

    # 합계 행
    total_row2 = len(store_stats) + 4
    ws2.row_dimensions[total_row2].height = 20
    totals2 = [
        "합계",
        sum(s["total"] for s in store_stats),
        sum(s["approved_cnt"] for s in store_stats),
        sum(s["rejected_cnt"] for s in store_stats),
        sum(s["total_compensation"] for s in store_stats),
    ]
    for col, val in enumerate(totals2, 1):
        cell = ws2.cell(total_row2, col, val)
        cell.font = Font(name="맑은 고딕", bold=True, size=10,
                         color=BRAND_RED if col == 5 else "333333")
        cell.fill = PatternFill("solid", fgColor="F0F0F0")
        cell.alignment = Alignment(
            horizontal="right" if col == 5 else ("center" if col > 1 else "left"),
            vertical="center"
        )
        cell.border = border
        if col == 5:
            cell.number_format = '#,##0'

    # 저장
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    from urllib.parse import quote
    filename_raw = f"iloom_보전금현황_{date.today().strftime('%Y%m%d')}.xlsx"
    filename_encoded = quote(filename_raw, safe="")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
    )


# ================================================================
# ERP 수주 API
# ================================================================
@app.post("/api/erp/upload")
async def upload_erp(file: UploadFile = File(...)):
    """ERP 수주 Excel 업로드 → 자동 분류 + 매칭"""
    import openpyxl
    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content))
    ws = wb.active

    headers = [str(c.value).strip() if c.value else "" for c in ws[1]]

    required = ["대리점", "수주번호", "수주상태", "주문일자", "수주건별금액", "납품처주소", "수주건명"]
    missing = [h for h in required if h not in headers]
    if missing:
        raise HTTPException(400, f"필수 컬럼 없음: {missing}")

    def ci(name: str) -> int | None:
        try:
            return headers.index(name)
        except ValueError:
            return None

    i_store = ci("대리점")
    i_no = ci("수주번호")
    i_status = ci("수주상태")
    i_name = ci("수주건명")
    i_date = ci("주문일자")
    i_delivery = ci("확정납기")
    i_amount = ci("수주건별금액")
    i_addr = ci("납품처주소")

    def to_date(v) -> str | None:
        if v is None:
            return None
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")
        return str(v)[:10]

    inserted = skipped = 0
    with get_db() as conn:
        for row in ws.iter_rows(min_row=2, values_only=True):
            order_no = row[i_no]
            store = row[i_store]
            if not order_no or not store:
                continue

            order_no = str(order_no).strip()
            store = str(store).strip()
            status = str(row[i_status]).strip() if row[i_status] else ""
            order_name = str(row[i_name]).strip() if row[i_name] else ""
            customer_name = extract_customer_name(order_name)
            base, seq = parse_order_no(order_no)
            store_type = "online" if store in ONLINE_STORES else "offline"
            order_date = to_date(row[i_date])
            delivery_date = to_date(row[i_delivery]) if i_delivery is not None else None
            amount = float(row[i_amount]) if row[i_amount] else 0.0
            address = str(row[i_addr]).strip() if row[i_addr] else None

            try:
                conn.execute("""
                    INSERT OR REPLACE INTO erp_orders
                    (order_no, order_base, order_seq, store_name, store_type, order_status,
                     customer_name, order_date, delivery_date, amount, address_dong)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (order_no, base, seq, store, store_type, status,
                      customer_name, order_date, delivery_date, amount, address))
                inserted += 1
            except Exception:
                skipped += 1

        classify_cancel_types(conn)
        matched = run_matching_engine(conn)

    return {
        "message": f"{inserted}건 처리, 취소분류 완료, 신규 매칭 {matched}건 발견",
        "inserted": inserted,
        "skipped": skipped,
        "matched": matched,
    }


@app.get("/api/erp/orders")
async def list_erp_orders(store_type: str = "", status: str = "", cancel_type: str = ""):
    with get_db() as conn:
        q = "SELECT * FROM erp_orders WHERE 1=1"
        params: list = []
        if store_type:
            q += " AND store_type=?"; params.append(store_type)
        if status:
            q += " AND order_status=?"; params.append(status)
        if cancel_type:
            q += " AND cancel_type=?"; params.append(cancel_type)
        q += " ORDER BY order_date DESC, order_no"
        rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/erp/stats")
async def erp_stats():
    with get_db() as conn:
        cancel_cnt = conn.execute(
            "SELECT COUNT(*) as c FROM erp_orders WHERE store_type='offline' AND cancel_type='pure_cancel'"
        ).fetchone()["c"]
        match_cnt = conn.execute("SELECT COUNT(*) as c FROM matches").fetchone()["c"]
        approved_cnt = conn.execute(
            "SELECT COUNT(*) as c FROM matches WHERE status='approved'"
        ).fetchone()["c"]
        total_comp = conn.execute(
            "SELECT COALESCE(SUM(compensation),0) as s FROM matches WHERE status='approved'"
        ).fetchone()["s"]
    return {
        "total_cancels": cancel_cnt,
        "total_matches": match_cnt,
        "approved_matches": approved_cnt,
        "total_compensation": total_comp,
    }


@app.post("/api/erp/run-match")
async def trigger_match():
    with get_db() as conn:
        matched = run_matching_engine(conn)
    return {"message": f"매칭 실행 완료: 신규 {matched}건 발견"}


# ================================================================
# 매칭 결과 API
# ================================================================
@app.get("/api/matches")
async def list_matches():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT
                m.id, m.offline_order_no, m.online_order_no,
                m.match_keys, m.match_confidence, m.result_type,
                m.compensation, m.status, m.created_at,
                off.store_name  AS offline_store,
                off.customer_name,
                off.address_dong,
                off.order_date  AS offline_date,
                off.amount      AS offline_amount,
                on_.store_name  AS online_store,
                on_.order_date  AS online_date,
                on_.amount      AS online_amount,
                e.event_name
            FROM matches m
            JOIN erp_orders off ON m.offline_order_no = off.order_no
            JOIN erp_orders on_ ON m.online_order_no  = on_.order_no
            LEFT JOIN events e  ON m.event_id = e.id
            ORDER BY m.created_at DESC
        """).fetchall()

        result = []
        for r in rows:
            d = dict(r)
            items = conn.execute(
                "SELECT * FROM match_items WHERE match_id=? ORDER BY id", (r["id"],)
            ).fetchall()
            d["items"] = [dict(i) for i in items]
            result.append(d)
    return result


@app.post("/api/matches/{match_id}/products")
async def verify_match_products(match_id: int, products: List[MatchProductIn]):
    """오프라인 취소 품목 입력 → 행사 품목과 매칭 → 보전금 계산"""
    if not products:
        raise HTTPException(400, "품목을 1개 이상 입력하세요")

    with get_db() as conn:
        match = conn.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
        if not match:
            raise HTTPException(404, "매칭 건을 찾을 수 없습니다")

        # 행사 품목 조회
        event_products = []
        if match["event_id"]:
            event_products = [
                dict(r) for r in conn.execute(
                    "SELECT * FROM event_products WHERE event_id=?", (match["event_id"],)
                ).fetchall()
            ]

        # 기존 품목 삭제 후 재저장
        conn.execute("DELETE FROM match_items WHERE match_id=?", (match_id,))

        product_dicts = [p.model_dump() for p in products]

        if event_products:
            matched = match_products(product_dicts, event_products)
        else:
            # 행사 미등록 시 전체 인정 처리 (수동 확인 필요 표시)
            matched = [{**p, "match_status": "approved"} for p in product_dicts]

        for mp in matched:
            conn.execute("""
                INSERT INTO match_items (match_id, product_name, series, category, amount, match_status)
                VALUES (?,?,?,?,?,?)
            """, (match_id, mp.get("product_name", ""), mp["series"],
                  mp["category"], mp.get("amount", 0), mp["match_status"]))

        result_type, compensation, note = calc_result_by_product(matched)

        conn.execute("""
            UPDATE matches SET result_type=?, compensation=?
            WHERE id=?
        """, (result_type, compensation, match_id))

    label = {"full": "✅ 전체 인정", "partial": "⚠️ 부분 인정", "rejected": "❌ 불인정"}
    return {
        "result_type": result_type,
        "compensation": compensation,
        "note": note,
        "products": matched,
        "message": label.get(result_type, "-"),
    }


@app.patch("/api/matches/{match_id}")
async def update_match(match_id: int, body: MatchStatusUpdate):
    if body.status not in ("pending", "approved", "rejected"):
        raise HTTPException(400, "status must be pending / approved / rejected")
    with get_db() as conn:
        conn.execute("UPDATE matches SET status=? WHERE id=?", (body.status, match_id))
    return {"message": "상태 업데이트 완료"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
