from __future__ import annotations

from pathlib import Path

from src.aruco_cube_gen.generate import generate_all

from ...artifacts import Artifact, artifact_from_path
from ...shared.manifest import write_manifest
from ..base import TargetRunResult
from .config import CubeTargetConfig


class CubeTarget:
    name = "cube"
    description = "Existing hollow cube plus marker plate outputs."

    def __init__(self, cfg: CubeTargetConfig | None = None) -> None:
        self.cfg = cfg or CubeTargetConfig()

    def generate(self) -> TargetRunResult:
        output_dir = Path(generate_all(self.cfg.legacy)).resolve()
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
