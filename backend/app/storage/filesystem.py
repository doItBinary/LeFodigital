from pathlib import Path
from uuid import uuid4


class FileSystemStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, suffix: str) -> str:
        stored_name = f"{uuid4().hex}{suffix.lower()}"
        target = self.root / stored_name
        target.write_bytes(content)
        return stored_name

    def path_for(self, stored_name: str) -> Path:
        target = (self.root / stored_name).resolve()
        if target.parent != self.root:
            raise ValueError("Invalid storage path")
        return target

    def delete(self, stored_name: str) -> None:
        target = self.path_for(stored_name)
        target.unlink(missing_ok=True)
