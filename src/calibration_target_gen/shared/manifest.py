from __future__ import annotations

import json
from pathlib import Path

from ..artifacts import Artifact


def write_manifest(
    output_dir: Path,
    target_name: str,
    artifacts: tuple[Artifact, ...],
) -> Path:
    manifest_path = output_dir / "manifest.json"
    payload = {
        "target": target_name,
        "output_dir": str(output_dir.resolve()),
        "artifacts": [artifact.to_dict() for artifact in artifacts],
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path
