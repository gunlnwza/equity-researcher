import asyncio
import subprocess
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from equity_researcher.render import compile_pdf, write_report


def test_write_report_awaits_openai_response():
    response = SimpleNamespace(output_text="Generated report")
    client = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(return_value=response))
    )

    result = asyncio.run(
        write_report(
            client,
            {
                "business_model": "First source",
                "competition": "Second source",
            },
        )
    )

    assert result == "Generated report"
    client.responses.create.assert_awaited_once()
    request = client.responses.create.await_args.kwargs
    content = request["input"][0]["content"]
    assert content[1]["text"] == "# business_model.md\n\nFirst source"
    assert content[2]["text"] == "# competition.md\n\nSecond source"


def test_compile_pdf_invokes_pandoc(tmp_path, monkeypatch):
    report_path = tmp_path / "report.md"
    report_path.write_text("# Equity research report")
    run = Mock()
    monkeypatch.setattr("equity_researcher.render.subprocess.run", run)

    output_path = compile_pdf(report_path)

    assert output_path == tmp_path / "report.pdf"
    run.assert_called_once_with(
        [
            "pandoc",
            str(report_path),
            "--output",
            str(output_path),
            "--pdf-engine=xelatex",
            "--variable",
            "geometry:margin=1in",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_compile_pdf_rejects_missing_report(tmp_path):
    with pytest.raises(FileNotFoundError, match="Report not found"):
        compile_pdf(tmp_path / "missing.md")


def test_compile_pdf_surfaces_pandoc_error(tmp_path, monkeypatch):
    report_path = tmp_path / "report.md"
    report_path.write_text("# Broken report")

    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=43,
            cmd="pandoc",
            stderr="LaTeX compilation failed",
        )

    monkeypatch.setattr("equity_researcher.render.subprocess.run", fail)

    with pytest.raises(RuntimeError, match="LaTeX compilation failed"):
        compile_pdf(report_path)
