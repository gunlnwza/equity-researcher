from pathlib import Path

DATA_DIR = Path("data/")
CONFIG_DIR = Path("config/")


class NoteRepository:
    """
    For accessing and saving notes.
    """

    def __init__(self, path: Path | str):
        self.path = DATA_DIR / path

    def rmdir(self):
        if not self.path.exists():
            return
        for file in self.path.glob("*"):
            file.unlink()
        self.path.rmdir()

    def get_topic_path(self, topic: str) -> Path:
        return Path(self.path / f"{topic}.md")

    def save(self, topic: str, text: str):
        self.path.mkdir(parents=True, exist_ok=True)
        with open(self.get_topic_path(topic), "w") as outfile:
            print(text, file=outfile)

    def have(self, topic: str) -> bool:
        return self.get_topic_path(topic).exists()
    
    def read(self, topic: str) -> str:
        return self.get_topic_path(topic).read_text()
