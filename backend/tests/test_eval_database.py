"""評估用資料庫：每次都是剛 seed 好、內容固定的獨立 SQLite 檔（ADR-0006）。"""
import sqlite3
from contextlib import closing

from evaluation.database import build_eval_db


def count(path, table):
    with closing(sqlite3.connect(path)) as conn:  # Windows 上沒關連線就刪不掉檔案
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_builds_a_fresh_seeded_database_at_the_given_path(tmp_path):
    path = tmp_path / "eval.db"
    build_eval_db(path)
    assert count(path, "bills_of_lading") == 50
    assert count(path, "freight_ledger") == count(path, "freight_charges") == 114


def test_rebuilding_replaces_whatever_was_there(tmp_path):
    path = tmp_path / "eval.db"
    build_eval_db(path)
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("DELETE FROM bills_of_lading WHERE id <= 10")
    build_eval_db(path)
    assert count(path, "bills_of_lading") == 50
