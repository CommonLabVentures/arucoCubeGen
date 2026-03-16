# ArUco Plate Target

This target generates a rectangular single-marker ArUco plate as two aligned STL bodies for multi-color printing workflows.

## Default Geometry

- White base plate: `83 mm x 220 mm x 4 mm`
- Marker: single centered `DICT_4X4_50` ArUco marker
- Marker ID: `0`
- Marker size: `83 mm` to maximize use of the limiting plate dimension
- Black pattern exported as a separate inlay body embedded `0.8 mm` into the top of the white plate
- Each run includes both a flat pattern preview and a shaded rendered preview

## Usage

```bash
python -m src.calibration_target_gen aruco_plate
```

## Output Artifacts

```text
out_aruco_plate_YYYY-MM-DD_HH-MM-SS/
├── aruco_plate_white.stl
├── aruco_plate_black.stl
├── aruco_plate_preview.png
├── aruco_plate_render.png
├── run_info.txt
└── manifest.json
```

Import the two STL files into Bambu Studio as parts of the same object, then assign the white and black filaments to the corresponding bodies.
