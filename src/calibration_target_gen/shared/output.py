from __future__ import annotations

from ..targets.base import TargetRunResult


def format_run_result(result: TargetRunResult) -> str:
    lines = [
        f"Target: {result.target_name}",
        f"Output directory: {result.output_dir}",
        "Artifacts:",
    ]
    for artifact in result.artifacts:
        lines.append(f"  - {artifact.name} [{artifact.kind}]")
    return "\n".join(lines)
