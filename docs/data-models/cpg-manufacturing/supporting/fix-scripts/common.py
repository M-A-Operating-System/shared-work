"""Shared helpers for the CPG manufacturing package fixes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

Json = Any
PKG = Path("/tmp/claude-0/-home-claude/4770b2d2-f54e-5ec8-aa89-f4fc7cefb22c/scratchpad/mfgwork")
TODAY = "2026-11-16"


def load(name: str) -> Json:
    return json.loads((PKG / f"{name}.json").read_text(encoding="utf-8"))


def save(name: str, data: Json) -> None:
    (PKG / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(r["id"]): r for r in rows}


def withdraw(row: dict[str, Any], reason: str) -> None:
    row["status"] = "withdrawn"
    row["withdrawn_reason"] = reason


def active(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("status", "active") == "active"]
