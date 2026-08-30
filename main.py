import yaml
from pathlib import Path
from pprint import pprint


def read_yaml(path: Path) -> dict:
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def read_config(config_path: Path) -> dict:
    analysis = read_yaml(config_path / "analysis.yaml")
    company = read_yaml(config_path / "company.yaml")
    questions = read_yaml(config_path / "questions.yaml")
    render = read_yaml(config_path / "render.yaml")

    config = {
        "analysis": analysis,
        "company": company,
        "questions": questions,
        "render": render
    }
    return config


config = read_config(Path("config"))

pprint(config)
