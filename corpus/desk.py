"""Policy Desk: live edits to the clinic's policy during a demo.

Two kinds of entry, kept in corpus/published.json:
  policy -- an approved change. It becomes a PolicyRecord that explicitly
            supersedes the record currently in force for that attribute.
  poison -- an unapproved document. It is indexed in Moss like any other, but
            no record backs it, so the gate never treats it as policy.
"""
from __future__ import annotations

import dataclasses
import json
import os
from datetime import datetime

from agent.gate.schema import PolicyRecord

PUBLISHED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "published.json")

# attribute -> (sentence template, allowed range). Only facts the extractor
# understands can be published; anything else would be unverifiable by design.
POLICY_FIELDS = {
    "fasting_duration": ("Fast for {v} hours before your appointment.", (1, 48)),
    "arrival_offset": ("Arrive {v} minutes early to complete check-in.", (1, 120)),
    "cost": ("A consultation visit costs ${v}.", (1, 5000)),
}


def normalize_value(attribute: str, value: float) -> str:
    return f"{value:.2f}" if attribute == "cost" else str(int(value))


def validate_policy(attribute: str, value: float) -> str:
    if attribute not in POLICY_FIELDS:
        raise ValueError(f"attribute must be one of {sorted(POLICY_FIELDS)}")
    lo, hi = POLICY_FIELDS[attribute][1]
    if not lo <= value <= hi:
        raise ValueError(f"{attribute} must be between {lo} and {hi}")
    return normalize_value(attribute, value)


def load_entries(path: str = PUBLISHED_PATH) -> list[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_entries(entries: list[dict], path: str = PUBLISHED_PATH) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(entries, f)
    os.replace(tmp, path)  # the worker never reads a half-written file


def _in_force(records: list[PolicyRecord], attribute: str, at: datetime) -> PolicyRecord | None:
    live = [r for r in records if r.attribute == attribute and r.is_active_at(at)]
    superseded = {r.supersedes for r in live if r.supersedes}
    live = [r for r in live if r.policy_id not in superseded]
    return live[0] if live else None


def apply_entries(base: list[PolicyRecord], entries: list[dict]) -> tuple[list[PolicyRecord], list[dict]]:
    """Returns (records, docs). docs are the Moss documents the entries need,
    as {'id', 'text'}. Entries are applied in order, so a later change
    supersedes an earlier one."""
    records = list(base)
    docs: list[dict] = []
    for n, e in enumerate(entries, 1):
        if e["kind"] == "poison":
            docs.append({"id": f"judge_upload_{n}.txt#note", "text": e["text"]})
            continue
        at = datetime.fromisoformat(e["at"])
        old = _in_force(records, e["attribute"], at)
        if old is None:
            continue
        template = POLICY_FIELDS[e["attribute"]][0]
        text = template.format(v=e["value"])
        new = dataclasses.replace(
            old,
            policy_id=f"desk-{n}-{e['attribute']}", source_id=f"policy_desk_{n}.txt",
            source_span=text, value=e["value"], effective_from=at, effective_to=None,
            supersedes=old.policy_id,
        )
        records[records.index(old)] = dataclasses.replace(old, effective_to=at)
        records.append(new)
        docs.append({"id": f"{new.source_id}#{new.attribute}", "text": text})
    return records, docs
