import yaml
from pathlib import Path


def read_yaml(path: Path | str) -> dict:
    with open(path, 'r') as file:
        return yaml.safe_load(file)


# def read_research_config(config_path: Path | str) -> dict:
#     config_path = Path(config_path)

#     analysis = read_yaml(config_path / "analysis.yaml")
    
#     company = read_yaml(config_path / "company.yaml")

#     questions = read_yaml(config_path / "questions.yaml")
#     # questions = read_yaml(config_path / "questions_small.yaml")

#     render = read_yaml(config_path / "render.yaml")

#     config = {
#         "analysis": analysis,
#         "company": company,
#         "questions": questions,
#         "render": render
#     }
#     return config
