import asyncio

import equity_researcher.evidence as evidence
from equity_researcher.evidence import NoteRepository


def test_search_all_questions_respects_concurrency_and_saves_files(
    tmp_path,
    monkeypatch,
):
    active_requests = 0
    peak_requests = 0

    async def fake_search_question(client, question, ticker):
        nonlocal active_requests, peak_requests
        active_requests += 1
        peak_requests = max(peak_requests, active_requests)
        await asyncio.sleep(0.01)
        active_requests -= 1
        return f"Evidence for {question['prompt']}"

    monkeypatch.setattr(evidence, "search_question", fake_search_question)
    repository = NoteRepository(tmp_path)
    questions = {
        f"topic_{number}": {"prompt": f"question {number}"}
        for number in range(5)
    }

    asyncio.run(
        evidence.search_all_questions(
            client=object(),
            evidence_repo=repository,
            questions=questions,
            ticker="NKE",
            concurrency=2,
        )
    )

    assert peak_requests == 2
    assert sorted(path.name for path in tmp_path.glob("*.md")) == [
        f"topic_{number}.md" for number in range(5)
    ]
    assert (tmp_path / "topic_3.md").read_text().strip() == (
        "Evidence for question 3"
    )


def test_search_all_questions_skips_cached_topics(tmp_path, monkeypatch):
    repository = NoteRepository(tmp_path)
    repository.save("cached", "Existing evidence")

    searched_topics = []

    async def fake_search_question(client, question, ticker):
        searched_topics.append(question["prompt"])
        return "Fresh evidence"

    monkeypatch.setattr(evidence, "search_question", fake_search_question)

    asyncio.run(
        evidence.search_all_questions(
            client=object(),
            evidence_repo=repository,
            questions={
                "cached": {"prompt": "do not search"},
                "new": {"prompt": "search this"},
            },
            ticker="NKE",
        )
    )

    assert searched_topics == ["search this"]
    assert (tmp_path / "cached.md").read_text().strip() == "Existing evidence"
    assert (tmp_path / "new.md").read_text().strip() == "Fresh evidence"
