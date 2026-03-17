# Printable A4 ArUco Sheet

This target generates a multi-page PDF for fast paper-based iteration before committing to 3D prints.

## Defaults

- Paper size: A4 portrait (`210 mm x 297 mm`)
- Marker size: `150 mm x 150 mm`
- Marker placement: centered on the page
- Dictionary: `DICT_4X4_50`
- Marker IDs: `0` through `15`
- Grid: `10 mm` spacing aligned to the marker origin

## Generate

```bash
python -m src.calibration_target_gen aruco_a4_sheet
```

Each run writes a timestamped output directory containing:

- a multi-page PDF with one marker per A4 page
- `run_info.txt`
- `manifest.json`

## Print Notes

- Print at `100%` or `Actual size`
- Disable `Fit to page`, `Shrink oversized pages`, or similar scaling options
- Use the PDF directly; do not re-export through tools that may resample or resize it
