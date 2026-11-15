"""資料字典 (Data Dictionary)：給人看也給 Agent 看（ticket 04、D3）。

- view.yaml：View + Dictionary 組（也是戰情室的預設），描述 freight_charges view。
- raw.yaml：Raw + Dictionary 組，描述原始運費帳 freight_ledger 與髒資料規則。
注入 prompt 時直接放 YAML 原文，只維護一份來源。
"""
from pathlib import Path
from typing import Literal

DICTIONARY_DIR = Path(__file__).resolve().parent.parent / "data_dictionary"

DictionaryVersion = Literal["view", "raw"]


def load_dictionary(version: DictionaryVersion) -> str:
    return (DICTIONARY_DIR / f"{version}.yaml").read_text(encoding="utf-8")
