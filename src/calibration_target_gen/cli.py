from __future__ import annotations

import argparse

from .registry import get_target, iter_targets
from .shared.output import format_run_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.calibration_target_gen",
        description="Generate calibration targets through a target-oriented entry point.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="cube",
        help="Target to generate. Defaults to 'cube'.",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="List available targets and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_targets:
        for target in iter_targets():
            print(f"{target.name}: {target.description}")
        return 0

    target = get_target(args.target)
    result = target.generate()
    print(format_run_result(result))
    return 0
