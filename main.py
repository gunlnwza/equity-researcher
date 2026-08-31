import asyncio
import os
import logging
from pathlib import Path
import argparse

from openai import AsyncOpenAI
from dotenv import load_dotenv

from equity_researcher.config import read_yaml, read_research_config, configure_logging
from equity_researcher.evidence import search_all_questions
from equity_researcher.note_repo import NoteRepository, DATA_DIR, CONFIG_DIR
from equity_researcher.render import write_report, compile_pdf

logger = logging.getLogger(__name__)

Questions = dict[str, str]
Evidences = dict[str, str]

async def write_and_save_report(client: AsyncOpenAI, evidence_repo: NoteRepository, output_repo: NoteRepository, questions: Questions):
    logger.info("Writing report")    
    evidences = {topic: evidence_repo.read(topic).strip() for topic in questions}

    report = await write_report(client, evidences)
    await asyncio.to_thread(output_repo.save, "report", report)
    logger.info("Saved report")


async def main() -> None:
    load_dotenv()
    configure_logging()

    concurrency = int(os.getenv("SEARCH_CONCURRENCY", "3"))
    if concurrency < 1:
        raise ValueError("SEARCH_CONCURRENCY must be at least 1")
    api_key = os.environ["OPENAI_API_KEY"]

    parser = argparse.ArgumentParser()
    parser.add_argument("ticker")
    parser.add_argument("-q", "--questions", required=True)

    args = parser.parse_args()
    ticker = args.ticker
    question_file = CONFIG_DIR / "questions" / f"{args.questions}.yaml"
    questions = read_yaml(question_file) or {}

    evidence_repo = NoteRepository(Path(ticker) / "evidence")
    output_repo = NoteRepository(Path(ticker) / "output")

    async with AsyncOpenAI(api_key=api_key) as client:
        await search_all_questions(
            client,
            evidence_repo,
            questions,
            ticker,
            concurrency=concurrency,
        )
        await write_and_save_report(client, evidence_repo, output_repo, questions)

    output_path = compile_pdf(output_repo.get_topic_path("report"))
    logger.info("Research complete")


if __name__ == "__main__":
    asyncio.run(main())
