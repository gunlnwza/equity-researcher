import logging
import asyncio

from openai import AsyncOpenAI

from .note_repo import NoteRepository

logger = logging.getLogger(__name__)


async def search_question(client: AsyncOpenAI, question: dict, ticker: str) -> str:
    """
    Ask gpt-5.6-luna to search on the web for the given question and ticker.
    """

    prompt = question["prompt"]

    model = "gpt-5.6-luna"
    assert model == "gpt-5.6-luna"

    response = await client.responses.create(
        model=model,
        tools=[
            {"type": "web_search"}
        ],
        input=f"""
Company: {ticker}

Research question:
{prompt}

Research this question and return a concise evidence-based answer.
""",
    )

    assert any(
        item.type == "web_search_call"
        for item in response.output
    )

    return response.output_text


async def search_all_questions(
    client: AsyncOpenAI,
    evidence_repo: NoteRepository,
    questions: dict,
    ticker: str,
    *,
    concurrency: int = 5,
) -> None:
    """
    Search all questions, skip all questions which already have a result.
    """

    semaphore = asyncio.Semaphore(concurrency)

    async def search_and_save(topic: str, question: dict) -> None:
        async with semaphore:
            logger.info("Searching topic=%s ticker=%s", topic, ticker)
            text = await search_question(client, question, ticker)
            await asyncio.to_thread(evidence_repo.save, topic, text)
            logger.info("Saved evidence topic=%s", topic)

    tasks = []
    for topic, question in questions.items():
        if evidence_repo.have(topic):
            continue
        tasks.append(search_and_save(topic, question))

    await asyncio.gather(*tasks)
