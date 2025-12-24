from pathlib import Path
from typing import BinaryIO
from .core.config import settings


class LocalStorage:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or settings.storage_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_obj: BinaryIO, filename: str) -> Path:
        target = self.base_dir / filename
        with target.open("wb") as f:
            f.write(file_obj.read())
        return target

    def open(self, filename: str) -> BinaryIO:
        return (self.base_dir / filename).open("rb")


storage = LocalStorage()
