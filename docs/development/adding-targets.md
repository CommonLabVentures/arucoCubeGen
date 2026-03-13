# Adding New Target Families

This repository is structured to support multiple robot workcell calibration targets without forcing all of them through the cube generator.

## Current Structure

```text
src/
  aruco_cube_gen/
  calibration_target_gen/
    artifacts.py
    cli.py
    registry.py
    shared/
    targets/
      cube/
```

## Intent

- Keep the existing cube generator stable
- Add new target families beside it, not inside it
- Share only the utilities that are genuinely cross-target
- Support non-STL outputs when needed

## Where New Code Should Go

For a new target family, add a new folder here:

```text
src/calibration_target_gen/targets/<target_name>/
```

Typical files for a new target:

- `config.py`
- `generate.py`
- `geometry.py` if the target has 3D geometry
- `exporters.py` if the target writes multiple output formats
- `__init__.py`

Shared code belongs here only if more than one target needs it:

```text
src/calibration_target_gen/shared/
```

Examples of shared code:

- marker image generation
- common output handling
- manifests
- reusable geometry primitives

## Registration

Register the target in:

- [src/calibration_target_gen/registry.py](/home/sambit/Code/arucoCubeGen/src/calibration_target_gen/registry.py)

The registry is the top-level dispatch point for the target-oriented CLI.

## Entry Points

General entry point:

```bash
python -m src.calibration_target_gen <target_name>
```

Cube compatibility entry point:

```bash
python -m src.aruco_cube_gen
```

## Output Model

New targets should think in terms of generated artifacts, not only STLs.

Depending on the target, outputs may include:

- STL
- SVG
- PDF
- PNG
- JSON metadata

The target-oriented package already includes artifact and manifest helpers for that direction.
