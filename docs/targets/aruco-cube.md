# ArUco Cube Target

This target generates a hollow calibration cube and matching ArUco marker plates for 3D printing.

## What It Produces

- Hollow cube with five recessed faces
- Matching press-fit marker plates
- Separate STL exports for cube, plate bases, marker geometry, and combined plates
- Run metadata for the generated set

## Quick Use

Target-oriented entry point:

```bash
python -m src.calibration_target_gen cube
```

Legacy cube-only entry point:

```bash
python -m src.aruco_cube_gen
```

## Core Geometry

- Outer cube edge: `150 mm`
- Wall thickness: `3.2 mm`
- Open bottom with retained rim
- Five recessed faces: `top`, `+X`, `-X`, `+Y`, `-Y`
- Recess depth matches plate thickness: `2.4 mm`
- Upright print orientation with the open bottom on the bed

## Plate Geometry

- Pure mitered plug geometry
- No bezel or flange
- No decorative overhangs
- Plates seat on 45 degree mitered slot walls

## Marker Geometry

- ArUco `4x4`
- Dictionary: `DICT_4X4_50`
- Border bits: `1`
- Raised black cells for two-color printing

## Typical Output Layout

```text
out_stls_YYYY-MM-DD_HH-MM-SS/
├── cube_with_slots.stl
├── plate_base.stl
├── plate_base_id5.stl
├── plate_marker_id5.stl
├── plate_combined_id5.stl
├── ...
├── run_info.txt
└── manifest.json
```

## Assembly

1. Press-fit the plates into the cube recesses.
2. Confirm each plate seats on the mitered walls and sits flush.
3. Add a small CA glue dot on back corners only if needed.
4. Use the cube with the open face down.

## Related Docs

- [Cube design notes](aruco-cube-design.md)
- [Adding new target families](../development/adding-targets.md)
