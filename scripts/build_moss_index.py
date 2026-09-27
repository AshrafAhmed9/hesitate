"""Creates the 'hesitate-clinic' Moss index: one document per policy sentence,
plus general patient-guide documents that have no policy record behind them
(corpus/patient_guide.py) -- these are what let the agent answer questions
the policy table was never meant to cover (parking, water while fasting,
medication) without the gate mistaking them for unverifiable policy claims.
    python -m scripts.build_moss_index
"""
import asyncio
import os

from dotenv import load_dotenv
from moss import DocumentInfo, MossClient

from agent.retrieval.adapter import build_record_docs
from corpus.patient_guide import GUIDE_DOCS
from corpus.policy_records import RECORDS

load_dotenv()
NAME = "hesitate-clinic"


async def main():
    client = MossClient(os.environ["MOSS_PROJECT_ID"], os.environ["MOSS_PROJECT_KEY"])
    existing = [getattr(i, "name", i) for i in await client.list_indexes()]
    print("existing indexes:", existing)
    if NAME in existing:
        await client.delete_index(NAME)
        print(f"deleted existing {NAME}")
    all_docs = build_record_docs(RECORDS) + GUIDE_DOCS
    docs = [DocumentInfo(id=d["id"], text=d["text"]) for d in all_docs]
    await client.create_index(NAME, docs)
    print(f"created {NAME} with {len(docs)} docs ({len(RECORDS)} policy, {len(GUIDE_DOCS)} guide)")


if __name__ == "__main__":
    asyncio.run(main())
