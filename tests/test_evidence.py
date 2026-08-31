import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from equity_researcher.evidence import search_question


def test_search_question_calls_openai_and_returns_text():
    response = SimpleNamespace(
        output=[SimpleNamespace(type="web_search_call")],
        output_text="Evidence-based answer",
    )
    client = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(return_value=response))
    )

    result = asyncio.run(
        search_question(
            client,
            {"prompt": "How does the company make money?"},
            "NKE",
        )
    )

    assert result == "Evidence-based answer"
    client.responses.create.assert_awaited_once()

    request = client.responses.create.await_args.kwargs
    assert request["model"] == "gpt-5.6-luna"
    assert request["tools"] == [{"type": "web_search"}]
    assert "Company: NKE" in request["input"]
    assert "How does the company make money?" in request["input"]

