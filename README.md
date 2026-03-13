# Robot Workcell Calibration Target Generator

This repository contains code for generating calibration targets used in robot workcells.

The long-term intent is to support multiple target families and output formats from one codebase. Right now, the implemented target family is an ArUco calibration cube with matching marker plates.

## Current Scope

- General target-oriented entry point: `src/calibration_target_gen`
- Existing cube generator kept intact: `src/aruco_cube_gen`
- Current implemented target: ArUco cube and marker plates

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.calibration_target_gen --list-targets
python -m src.calibration_target_gen cube
```

The original cube entry point still works:

```bash
python -m src.aruco_cube_gen
```

## Documentation

- [ArUco cube target guide](docs/targets/aruco-cube.md)
- [ArUco cube design notes](docs/targets/aruco-cube-design.md)
- [Adding new target families](docs/development/adding-targets.md)

## Repository Layout

```text
src/
  aruco_cube_gen/          Legacy cube implementation
  calibration_target_gen/  Target-oriented package for multi-target support
docs/
  targets/
  development/
```

## Outputs

Each generator run writes a timestamped output directory. The exact artifacts depend on the selected target and may include meshes, images, documents, and metadata.

## License

MIT License
