from __future__ import annotations

from pathlib import Path

from ...artifacts import Artifact, artifact_from_path
from ...shared.manifest import write_manifest
from ..base import TargetRunResult
from .config import CharucoPlateConfig
from .generate import generate_all


class CharucoPlateTarget:
    name = "charuco_plate"
    description = "Square 3x3 ChArUco plate with separate white and black AMS-ready STL bodies."

    def __init__(self, cfg: CharucoPlateConfig | None = None) -> None:
        self.cfg = cfg or CharucoPlateConfig()

    def generate(self) -> TargetRunResult:
        output_dir = generate_all(self.cfg).resolve()
        artifacts = _collect_artifacts(output_dir)
        manifest_path = write_manifest(output_dir, self.name, artifacts)
        manifest_artifact = artifact_from_path(manifest_path, description="Artifact manifest")
        return TargetRunResult(
            target_name=self.name,
            output_dir=output_dir,
            artifacts=tuple((*artifacts, manifest_artifact)),
        )


def _collect_artifacts(output_dir: Path) -> tuple[Artifact, ...]:
    files = [path for path in output_dir.iterdir() if path.is_file()]
    files.sort(key=lambda path: path.name)
    return tuple(artifact_from_path(path) for path in files)
