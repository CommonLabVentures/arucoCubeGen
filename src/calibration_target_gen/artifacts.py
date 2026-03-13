from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


_SUFFIX_TO_KIND = {
    ".json": "manifest",
    ".png": "image",
    ".pdf": "document",
    ".stl": "mesh",
    ".svg": "vector",
    ".txt": "text",
}


@dataclass(frozen=True)
class Artifact:
    path: Path
    kind: str
    description: str = ""

    @property
    def name(self) -> str:
        return self.path.name

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": str(self.path),
            "kind": self.kind,
            "description": self.description,
        }


def artifact_from_path(path: Path, description: str = "") -> Artifact:
    kind = _SUFFIX_TO_KIND.get(path.suffix.lower(), "file")
    return Artifact(path=path.resolve(), kind=kind, description=description)
