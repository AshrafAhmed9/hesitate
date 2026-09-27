"""Creates the 'hesitate-clinic' Moss index: one document per policy sentence.
    python -m scripts.build_moss_index
"""
import asyncio
import os

from dotenv import load_dotenv
from moss import DocumentInfo, MossClient

from agent.retrieval.adapter import build_record_docs
from corpus.policy_records import RECORDS

load_dotenv()
NAME = "hesitate-clinic"


async def main():
    client = MossClient(os.environ["MOSS_PROJECT_ID"], os.environ["MOSS_PROJECT_KEY"])
    print("existing indexes:", [getattr(i, "name", i) for i in await client.list_indexes()])
    docs = [DocumentInfo(id=d["id"], text=d["text"]) for d in build_record_docs(RECORDS)]
    await client.create_index(NAME, docs)
    print(f"created {NAME} with {len(docs)} docs")


if __name__ == "__main__":
    asyncio.run(main())
