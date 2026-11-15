"""評估集跑分（ticket 06、ADR-0006）。

三個對照組 (Arm) × 20 題 × 每題 3 次。每次取 Agent 最後一句執行的 SQL，在剛 seed 好的獨立
SQLite 檔上重跑，拿結果比對標準答案。輸出逐次明細 (JSON) 與報告 (Markdown)。

    cd backend
    python -m evaluation.run_eval                  # 全部跑
    python -m evaluation.run_eval --only CN-1 --arms "View + Dictionary" --runs 1   # 冒煙測試
"""
import argparse
import asyncio
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from db.database import create_readonly_engine
from evaluation.database import build_eval_db
from evaluation.questions import QUESTIONS, Question
from evaluation.scoring import score
from services.sql_agent_service import WAR_ROOM_ARM, Arm, stream_sql_agent
from services.sql_guard import run_guarded_query

RAW_TABLES = ("bills_of_lading", "freight_ledger", "customer_aliases", "fx_rates")
ARMS = {
    "Raw": Arm(allowed_tables=RAW_TABLES, dictionary=None),
    "Raw + Dictionary": Arm(allowed_tables=RAW_TABLES, dictionary="raw"),
    "View + Dictionary": WAR_ROOM_ARM,
}
RESULTS_DIR = Path(__file__).resolve().parent / "results"
MODEL = "gpt-4o-mini"  # 與 services/sql_agent_service.py 一致


@dataclass
class Record:
    arm: str
    qid: str
    trap: str
    run: int
    correct: bool
    reason: str  # correct / wrong_result / sql_error / no_sql / agent_error
    sql: Optional[str]
    answer: Optional[str]


async def run_once(question: Question, arm_name: str, run: int, engine) -> Record:
    arm = ARMS[arm_name]
    last_sql, answer = None, None
    try:
        async for event in stream_sql_agent(question.text, engine, arm):
            if event.get("sql"):
                last_sql = event["sql"]
            if event["event"] == "message":
                answer = event["data"]
    except Exception as e:  # Agent 本身出錯（逾時、API 錯誤）也算這次答錯
        return Record(arm_name, question.qid, question.trap, run, False, "agent_error", last_sql, f"{type(e).__name__}: {e}")

    if last_sql is None:
        return Record(arm_name, question.qid, question.trap, run, False, "no_sql", None, answer)
    try:
        _, rows, _ = run_guarded_query(engine, last_sql, arm.allowed_tables)
    except Exception:
        return Record(arm_name, question.qid, question.trap, run, False, "sql_error", last_sql, answer)
    correct = score(rows, question.gold)
    return Record(arm_name, question.qid, question.trap, run, correct, "correct" if correct else "wrong_result", last_sql, answer)


async def run_all(questions, arm_names, runs: int, concurrency: int, engine) -> list[Record]:
    semaphore = asyncio.Semaphore(concurrency)
    jobs = [(q, a, r) for a in arm_names for q in questions for r in range(1, runs + 1)]
    done = 0

    async def guarded(q, a, r):
        nonlocal done
        async with semaphore:
            record = await run_once(q, a, r, engine)
        done += 1
        print(f"[{done}/{len(jobs)}] {a} {q.qid} #{r}: {record.reason}", flush=True)
        return record

    return await asyncio.gather(*(guarded(q, a, r) for q, a, r in jobs))


def summarize(records: list[Record]) -> dict:
    """每組：答對次數、總次數、穩定答對題數（每次都對）、依陷阱 (答對, 總次數)、失敗原因分布。"""
    summary = {}
    for arm in dict.fromkeys(r.arm for r in records):
        mine = [r for r in records if r.arm == arm]
        per_question = defaultdict(list)
        by_trap = defaultdict(lambda: [0, 0])
        for r in mine:
            per_question[r.qid].append(r.correct)
            by_trap[r.trap][0] += r.correct
            by_trap[r.trap][1] += 1
        summary[arm] = {
            "correct": sum(r.correct for r in mine),
            "total": len(mine),
            "stable": sum(all(results) for results in per_question.values()),
            "questions": len(per_question),
            "by_trap": {trap: tuple(v) for trap, v in by_trap.items()},
            "per_question": {qid: results for qid, results in per_question.items()},
            "reasons": dict(sorted(Counter(r.reason for r in mine).items())),
        }
    return summary


def _pct(correct: int, total: int) -> str:
    return f"{correct}/{total}（{correct / total:.0%}）" if total else "—"


def render_report(summary: dict, meta: dict) -> str:
    arms = list(summary)
    traps = list(dict.fromkeys(q.trap for q in QUESTIONS))
    lines = [
        f"# 評估報告 {meta['date']}",
        "",
        f"- 模型：{meta['model']}；每題每組跑 {meta['runs']} 次；commit `{meta['commit']}`",
        "- 資料：01 固定提單 50 張＋02 運費帳 114 筆，評估前重建於獨立 SQLite 檔",
        "- 判分：Agent 最後一句 SQL 在評估資料庫重跑，比對從乾淨原始資料算出的標準答案（數字 ±0.01，集合不看順序）",
        "",
        "## 整體",
        "",
        "| 對照組 | 答對率（每次分開算） | 穩定答對（每次都對）的題數 |",
        "|---|---|---|",
    ]
    for arm in arms:
        s = summary[arm]
        lines.append(f"| {arm} | {_pct(s['correct'], s['total'])} | {s['stable']}/{s['questions']} |")
    lines += ["", "## 依陷阱類型", "", "| 陷阱 | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for trap in traps:
        cells = [_pct(*summary[arm]["by_trap"].get(trap, (0, 0))) for arm in arms]
        lines.append(f"| {trap} | " + " | ".join(cells) + " |")
    lines += ["", "## 逐題（✅ 對、❌ 錯，依每次執行順序）", "", "| 題目 | 陷阱 | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for q in QUESTIONS:
        if not any(q.qid in summary[arm]["per_question"] for arm in arms):
            continue
        cells = ["".join("✅" if ok else "❌" for ok in summary[arm]["per_question"].get(q.qid, [])) for arm in arms]
        lines.append(f"| {q.qid} {q.text} | {q.trap} | " + " | ".join(cells) + " |")
    lines += ["", "## 答錯原因", "", "| 對照組 | 原因分布 |", "|---|---|"]
    for arm in arms:
        reasons = ", ".join(f"{k} {v}" for k, v in summary[arm]["reasons"].items() if k != "correct") or "—"
        lines.append(f"| {arm} | {reasons} |")
    lines += [
        "",
        "原因說明：wrong_result＝SQL 跑得出結果但不對；sql_error＝SQL 被防護擋下或執行失敗；"
        "no_sql＝沒有執行任何 SQL；agent_error＝Agent 本身出錯（逾時、API 錯誤）。",
        "",
        "## 已知限制",
        "",
        "- 只看 SQL 結果：Agent 查對但在自然語言摘要裡寫錯數字，仍判為正確（ADR-0006）。",
        "- 只看最後一句 SQL：Agent 分多句查詢再自行合併計算時，會被判錯。",
        "- 陷阱分類是「主要考點」：Raw 組的同一題常同時碰到多幣別、客戶別名等多個陷阱。",
        "- 資料字典曾用 3 題（9 月運費、Apple 總運費、請款遠超報價）手動調整；評估集刻意避開這 3 題，"
        "但 UM-1（Tesla 一共被請款多少）和「Apple 的總運費」考的是同一條規則。",
    ]
    return "\n".join(lines) + "\n"


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="評估集跑分")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--only", nargs="*", help="只跑這些題號")
    parser.add_argument("--arms", nargs="*", choices=list(ARMS), default=list(ARMS))
    parser.add_argument("--no-report", action="store_true", help="不寫 Markdown 報告（冒煙測試用）")
    args = parser.parse_args()

    questions = [q for q in QUESTIONS if not args.only or q.qid in args.only]
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "eval.db"
        build_eval_db(db_path)
        engine = create_readonly_engine(str(db_path))
        try:
            records = asyncio.run(run_all(questions, args.arms, args.runs, args.concurrency, engine))
        finally:
            engine.dispose()

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    meta = {"date": stamp, "model": MODEL, "runs": args.runs, "commit": _commit()}
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / f"{stamp}.json").write_text(
        json.dumps({"meta": meta, "records": [asdict(r) for r in records]}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = summarize(records)
    for arm, s in summary.items():
        print(f"{arm}: {_pct(s['correct'], s['total'])}，穩定答對 {s['stable']}/{s['questions']}")
    if not args.no_report:
        report = RESULTS_DIR / f"{stamp}.md"
        report.write_text(render_report(summary, meta), encoding="utf-8")
        print(f"報告：{report}")


if __name__ == "__main__":
    main()
