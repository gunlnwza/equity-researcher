# Research configuration

The `questions/` directory contains named sets of equity-research questions.
Select a set with the `--questions` (`-q`) command-line argument:

```bash
python main.py NKE --questions example
python main.py NKE -q small
```

The argument is a configuration name, not a path. For example, `-q small`
loads `config/questions/small.yaml`.

## Question format

Each file is a YAML mapping. The key becomes the evidence filename and the
`prompt` is sent to the research model.

```yaml
business_model:
  prompt: |
    How does the company make money?

competition:
  prompt: |
    Who are the company's major competitors
    and what determines competitive advantage?
```

This configuration produces:

```text
data/<TICKER>/evidence/business_model.md
data/<TICKER>/evidence/competition.md
```

Keep topic keys unique and filename-safe. Prefer lowercase `snake_case` names
because each key is used directly as a Markdown filename.

## Included question sets

| Name | Purpose |
| --- | --- |
| `example` | Full question set from the project proposal. |
| `small` | Only business model and competition; useful for faster, cheaper test runs. |
| `none` | Empty set used to test whether the report writer avoids inventing evidence. |

An empty YAML file is parsed as `None`. The CLI normalizes it to an empty
mapping with:

```python
questions = read_yaml(question_file) or {}
```

An empty mapping is used instead of an empty list because the research pipeline
expects topic-to-question pairs and iterates over `questions.items()`.

## Adding a question set

1. Create `config/questions/<name>.yaml`.
2. Add one or more topic mappings using the schema above.
3. Run it with `python main.py <TICKER> -q <name>`.

Evidence already present for a topic is reused. Delete or relocate that topic's
file under `data/<TICKER>/evidence/` when you intentionally want fresh research.
