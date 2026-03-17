# Robot Workcell Calibration Target Generator

This repository contains code for generating calibration targets used in robot workcells.

The long-term intent is to support multiple target families and output formats from one codebase. The current implemented targets are an ArUco calibration cube with matching marker plates, a rectangular single-marker ArUco plate, a square ChArUco plate, and printable A4 ArUco marker sheets.

## Current Scope

- General target-oriented entry point: `src/calibration_target_gen`
- Existing cube generator kept intact: `src/aruco_cube_gen`
- Current implemented targets:
  - ArUco cube and marker plates
  - Rectangular single-marker ArUco plate with separate white and black STL bodies
  - Square ChArUco plate with separate white and black STL bodies
  - Printable A4 ArUco marker sheets in PDF format

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.calibration_target_gen --list-targets
python -m src.calibration_target_gen cube
python -m src.calibration_target_gen aruco_a4_sheet
python -m src.calibration_target_gen aruco_plate
python -m src.calibration_target_gen charuco_plate
```

The original cube entry point still works:

```bash
python -m src.aruco_cube_gen
```

## Documentation

- [ArUco cube target guide](docs/targets/aruco-cube.md)
- [ArUco plate target guide](docs/targets/aruco-plate.md)
- [Printable A4 ArUco sheet guide](docs/targets/aruco-a4-sheet.md)
- [ArUco cube design notes](docs/targets/aruco-cube-design.md)
- [ChArUco plate target guide](docs/targets/charuco-plate.md)
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
