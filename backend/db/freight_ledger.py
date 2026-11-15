"""運費帳 (Freight Ledger) 的原樣載入、參考表與清理用的 view（ticket 03、D1）。

- freight_ledger：財務系統匯出檔原樣載入，全 TEXT、內容一字不改；只在表不存在時載入。
- customer_aliases：別名 → 標準 Shipper 名稱（參考表，每次載入都重建）。
- fx_rates：月匯率，每 1 USD 可換多少該幣別（參考表，每次載入都重建）。
- freight_charges：一段 SQL 完成全部清理（可稽核、原始資料不動）；每次載入都重建，
  改了清理邏輯只要重新部署就生效。
"""
import csv
from pathlib import Path

from sqlalchemy import Engine, inspect, text

SOURCE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"
RAW_COLUMNS = ["BL_NO", "CUSTOMER", "CHG_CODE", "AMOUNT", "INV_DATE"]


FREIGHT_CHARGES_VIEW = """
CREATE VIEW freight_charges AS
WITH bills AS (
    -- 提單主表可能被重複上傳同一張提單；先收斂成一張一列，避免 join 後費用被重複計算
    SELECT bl_number, MIN(on_board_date) AS on_board_date
    FROM bills_of_lading
    GROUP BY bl_number
),
normalized AS (
    SELECT
        l.*,
        UPPER(REPLACE(REPLACE(TRIM(l.BL_NO), ' ', ''), '-', '')) AS norm_bl_number,
        TRIM(l.INV_DATE) AS d,
        UPPER(TRIM(l.AMOUNT)) AS amt
    FROM freight_ledger AS l
),
parsed AS (
    SELECT
        n.*,
        CASE
            -- 20260311
            WHEN d GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
                THEN substr(d, 1, 4) || '-' || substr(d, 5, 2) || '-' || substr(d, 7, 2)
            -- 2026.03.11
            WHEN d GLOB '[0-9][0-9][0-9][0-9].[0-9][0-9].[0-9][0-9]'
                THEN REPLACE(d, '.', '-')
            -- 11-Mar-26
            WHEN d GLOB '[0-9][0-9]-[A-Z][a-z][a-z]-[0-9][0-9]'
                THEN '20' || substr(d, 8, 2) || '-'
                    || printf('%02d', (instr('JanFebMarAprMayJunJulAugSepOctNovDec', substr(d, 4, 3)) + 2) / 3)
                    || '-' || substr(d, 1, 2)
            -- 2026/3/11（月、日不補零）
            WHEN d GLOB '[0-9][0-9][0-9][0-9]/*/*'
                THEN printf('%s-%02d-%02d',
                    substr(d, 1, 4),
                    CAST(substr(d, 6, instr(substr(d, 6), '/') - 1) AS INTEGER),
                    CAST(substr(substr(d, 6), instr(substr(d, 6), '/') + 1) AS INTEGER))
        END AS invoice_date,
        CASE
            WHEN amt LIKE '%USD%' OR amt LIKE '%US$%' THEN 'USD'
            WHEN amt LIKE '%TWD%' OR amt LIKE '%NT$%' THEN 'TWD'
            WHEN amt LIKE '%EUR%' OR amt LIKE '%€%' THEN 'EUR'
            WHEN amt LIKE '%JPY%' OR amt LIKE '%¥%' THEN 'JPY'
        END AS currency,
        -- 去掉幣別、千分位、空白與正負號標記，只留數字；正負號下面另依費用代碼決定
        ABS(CAST(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                amt, 'USD', ''), 'US$', ''), 'NT$', ''), 'TWD', ''), 'EUR', ''), 'JPY', ''), '€', ''), '¥', ''),
                ',', ''), ' ', ''), '(', ''), ')', ''), '-', '')
        AS REAL)) AS abs_amount
    FROM normalized AS n
)
SELECT
    p.BL_NO AS raw_bl_number,
    p.norm_bl_number AS bl_number,
    CASE
        WHEN b.bl_number IS NULL THEN 'unmatched'  -- 對不上的列保留，不丟掉
        WHEN p.BL_NO = b.bl_number THEN 'matched'
        ELSE 'normalized_match'
    END AS match_status,
    p.CUSTOMER AS raw_customer,
    COALESCE(a.shipper, TRIM(p.CUSTOMER)) AS customer,  -- 沒對到別名：保留原名，不變 NULL
    CASE WHEN a.shipper IS NULL THEN 1 ELSE 0 END AS is_unmapped_customer,
    p.CHG_CODE AS charge_code,
    p.CHG_CODE = 'CN' AS is_credit_note,
    p.AMOUNT AS raw_amount,
    p.currency,
    -- Credit Note 不論原始寫正數、-500 或 (500.00)，一律為負
    CASE WHEN p.CHG_CODE = 'CN' THEN -p.abs_amount ELSE p.abs_amount END AS amount,
    -- 依發票月份匯率換成 USD；Billed Amount = 同一張提單的 SUM(amount_usd)
    CASE WHEN p.CHG_CODE = 'CN' THEN -p.abs_amount ELSE p.abs_amount END / f.units_per_usd AS amount_usd,
    p.INV_DATE AS raw_invoice_date,
    p.invoice_date,
    b.on_board_date
FROM parsed AS p
LEFT JOIN bills AS b ON b.bl_number = p.norm_bl_number
LEFT JOIN customer_aliases AS a ON a.alias = TRIM(p.CUSTOMER)
LEFT JOIN fx_rates AS f ON f.month = substr(p.invoice_date, 1, 7) AND f.currency = p.currency
"""

REFERENCE_TABLES = {
    # 表名: (建表 SQL, 來源 CSV)
    "customer_aliases": (
        "CREATE TABLE customer_aliases (alias TEXT PRIMARY KEY, shipper TEXT NOT NULL)",
        "customer_aliases.csv",
    ),
    "fx_rates": (
        "CREATE TABLE fx_rates (month TEXT, currency TEXT, units_per_usd REAL NOT NULL, PRIMARY KEY (month, currency))",
        "fx_rates.csv",
    ),
}


def _read_csv(name: str) -> list[dict]:
    with (SOURCE_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_freight_ledger(engine: Engine, reload: bool = False) -> None:
    """建立運費帳相關的表與 view。App 啟動時呼叫（冪等）；reload=True 會重新載入原始運費帳。"""
    with engine.begin() as conn:
        if reload:
            conn.execute(text("DROP TABLE IF EXISTS freight_ledger"))
        if not inspect(conn).has_table("freight_ledger"):
            conn.execute(text(f"CREATE TABLE freight_ledger ({', '.join(f'{c} TEXT' for c in RAW_COLUMNS)})"))
            conn.execute(
                text(f"INSERT INTO freight_ledger VALUES ({', '.join(f':{c}' for c in RAW_COLUMNS)})"),
                _read_csv("freight_ledger_export.csv"),
            )
        conn.execute(text("DROP VIEW IF EXISTS freight_charges"))
        for table, (create_sql, source) in REFERENCE_TABLES.items():
            rows = _read_csv(source)
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.execute(text(create_sql))
            conn.execute(text(f"INSERT INTO {table} VALUES ({', '.join(':' + c for c in rows[0])})"), rows)
        conn.execute(text(FREIGHT_CHARGES_VIEW))
