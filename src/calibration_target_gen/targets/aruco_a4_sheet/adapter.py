from __future__ import annotations

from pathlib import Path

from ...artifacts import Artifact, artifact_from_path
from ...shared.manifest import write_manifest
from ..base import TargetRunResult
from .config import ArucoA4SheetConfig
from .generate import generate_all


class ArucoA4SheetTarget:
    name = "aruco_a4_sheet"
    description = "Multi-page printable A4 ArUco marker sheets with a centered 150 mm marker and 10 mm grid."

    def __init__(self, cfg: ArucoA4SheetConfig | None = None) -> None:
        self.cfg = cfg or ArucoA4SheetConfig()

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
