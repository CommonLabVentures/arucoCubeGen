<!--
Purpose: Maintain a diff-grounded, per-commit project history timeline for this repository.
Use git committer timestamps, not author timestamps.
Inspect actual diffs, touched files, and code/docs structure; do not rely on commit subjects alone.
Append only new commits when updating this file.
Preserve chronological order.
Keep exactly one entry per commit.
Do not rewrite older entries unless correcting a factual error.
Header format: ## <ISO-8601 committer timestamp> | <7-char sha> | <author>
Subject format: **Subject:** `<full commit subject>`
-->
# Project Timeline

This document reconstructs repository history from git diffs, touched files, and code/docs changes rather than commit messages alone.
Timestamps use git committer time.
Entries are listed in chronological order.

## 2025-12-11T15:29:12+08:00 | 12b55c3 | Pal Sambit
**Subject:** `first commit`
The repository was initialized with only `README.md`, and that file contained just the `# arucoCubeGen` title. No generator code, configuration, or assets were present yet.

## 2025-12-11T18:40:29+08:00 | 1eabfa7 | Pal Sambit
**Subject:** `working commit with readme`
This added the first working implementation as a single `aruco_cube_stls.py` script and expanded the README into full usage documentation. The script generated a hollow 120 mm cube with five recessed faces, a reusable plate base, raised-cell ArUco marker meshes, and combined STL exports for marker IDs `0` through `4`, all driven by module-level constants.

## 2025-12-11T18:54:54+08:00 | 45be054 | Pal Sambit
**Subject:** `added render of cube`
This was a documentation-and-assets update: it added `images/cube_render.png` and inserted a preview section into the README so the cube geometry could be shown visually. The generator code did not change.

## 2025-12-11T19:04:23+08:00 | 4d00460 | Pal Sambit
**Subject:** `added render of plate`
This extended the README preview table with `images/plate_render.png` so both the cube and the plate were illustrated. No source files changed.

## 2025-12-18T10:25:12+08:00 | 486da84 | Pal Sambit
**Subject:** `Add seam-hiding bezel to ArUco plates and tune marker layout for 1.5m detection. Adds a thin top-face bezel (flange) to overlap the cube slot opening and hide seam/shadow lines while allowing face-up printing on the P2S textured plate. Introduces BEZEL_OVERHANG and BEZEL_THICKNESS parameters and updates create_plate_base() to generate a plug + bezel geometry. Reduces PLATE_MARGIN_FRACTION to 0.88 to improve the white quiet zone without shrinking the marker excessively. Explicitly passes ARUCO_BORDER_BITS to OpenCV marker generation to match detector assumptions. Intended for matte PLA, 0.12–0.16 mm layers, support-free printing. Improves ArUco detection robustness up to ~1.5 m with Intel RealSense D455 RGB.`
This introduced `.gitignore` rules for generated meshes, output folders, virtual environments, and slicer artifacts, then changed plate generation so the base became a plug plus a thin top-face bezel flange. The script also reduced `PLATE_MARGIN_FRACTION` from `0.9` to `0.88` and started passing `borderBits` into OpenCV marker rendering, which tightened the quiet zone and aligned the generated marker image with detector assumptions.

## 2025-12-18T10:32:00+08:00 | 62f0aa8 | Pal Sambit
**Subject:** `revised readme, to explain the design rationale`
This was primarily a README rewrite that shifted the documentation from setup notes toward design rationale. It added D455 camera assumptions, pixels-per-cell calculations, 1.5 m marker sizing math, quiet-zone analysis, and an explanation of why the bezel helped detection, while simplifying or removing the earlier installation and troubleshooting emphasis.

## 2025-12-18T10:39:44+08:00 | 5abde96 | Pal Sambit
**Subject:** `printing instructions added to readme`
This reorganized the README again into a more operational guide: it kept the sizing rationale, but restored explicit run instructions, detailed Bambu Studio/AMS import and print workflow steps, assembly notes, and troubleshooting commands. The code was unchanged.

## 2025-12-18T11:04:03+08:00 | be84da9 | Pal Sambit
**Subject:** `added plate ID text`
The monolithic script gained per-ID plate labeling. `create_plate_base()` now accepted text and added sizing, placement, engraving, and emboss-fallback logic for IDs in the white band, and the export loop switched from reusing one base to generating per-ID base meshes plus matching combined exports.

## 2025-12-18T16:18:12+08:00 | 87ce7b7 | Pal Sambit
**Subject:** `Refactor project structure; modularize geometry and ArUco generation, add timestamped outputs and run metadata`
This deleted the root `aruco_cube_stls.py` script and split the generator into the `src/aruco_cube_gen` package with separate modules for config, geometry, marker generation, text mesh creation, output handling, orchestration, and a `__main__.py` entry point. Operationally it changed invocation to `python -m src.aruco_cube_gen`, added `requirements.txt`, wrote each run into a timestamped output directory, emitted `run_info.txt`, and replaced the earlier text path with a modular helper that included a rasterized fallback.

## 2025-12-18T16:25:54+08:00 | b146c97 | Pal Sambit
**Subject:** `improvements to text to avoid being removed by slicer`
This was a small printability follow-up for plate IDs: the raster text fallback used thicker strokes and a lower target pixel height, and the embossed text was embedded `0.25 mm` into the plate surface so slicers were less likely to discard it as separate or paper-thin geometry.

## 2025-12-18T16:37:04+08:00 | 581299e | Pal Sambit
**Subject:** `some text tweaks to escape dodgy slicer`
This hardened the text geometry further by increasing `bezel_text_depth_mm` from `0.8` to `1.2`, increasing the surface overlap to `0.5 mm`, switching raster text from antialiased `LINE_AA` output to `LINE_8`, and adding close-plus-dilate morphology before extrusion. The change was entirely about making the embossed IDs survive slicer cleanup.

## 2025-12-18T17:11:58+08:00 | 3107785 | Pal Sambit
**Subject:** `Improve cube printability: chamfer slot openings and add internal roof ribs to reduce bridging`
This retuned the cube around a larger, lighter shell: `cube_edge` became `150 mm`, wall thickness dropped to `3.2 mm`, slot fraction increased to `0.85`, slot depth became `2.4 mm`, and the bottom could be opened while keeping a rim. Geometry generation replaced plain slot boxes with chamfered slot cutters and added optional internal roof ribs, so the cube gained explicit support-free printability features while preserving the same overall export flow.

## 2025-12-18T18:17:00+08:00 | b4bf3e7 | Pal Sambit
**Subject:** `tweaks for long bridge and updated readme`
This refined the bridge-focused iteration by adding `roof_gusset_mm`, refactoring open-bottom, rib, gusset, and slot-cutter logic into dedicated helpers, and turning the chamfered slot cutters and their union into boolean-built solids instead of plain concatenations. The README and committed render images were updated in parallel to describe the 150 mm open-bottom cube, the expected Bambu bridge warning, and the recommended bridge-speed tuning.

## 2025-12-19T01:15:18+08:00 | cf417b3 | Pal Sambit
**Subject:** `attic keepout, roof stiffening, and tapered slot geometry`
This replaced the chamfered-box slot system with true tapered prism slot geometry and made the plate plug taper match the slot profile. The cube also gained an inside-only roof-thickener slab, attic-style support slopes, and a keepout around the top slot so those additive solids would not refill the slot cavity, while config and README were reorganized around the new roof and taper parameters.

## 2025-12-24T11:57:08+08:00 | 8df845c | Pal Sambit
**Subject:** `remove top roof; add open top slot with mitered seat and gradual 45deg internal support ramp`
This removed the attic and roof-thickener approach and changed the top-face strategy entirely. The top slot was still cut like the side faces, but the flat slot floor was then removed so the top became open while the mitered seating walls remained, and a new additive-only 45° perimeter support ramp was added below the opening; the cube README was also moved from the repository root into `src/aruco_cube_gen/README.md`.

## 2025-12-24T11:59:51+08:00 | 1480e45 | Pal Sambit
**Subject:** `added some historical info in README`
This was mostly a documentation expansion: it appended a long `Design Evolution & Lessons Learned` section to the cube README documenting the rejected flat-roof and attic experiments and the reasoning behind the open-top solution. The only code-side change was a commented alternate `plate_ids` line in `config.py`.

## 2025-12-24T12:19:49+08:00 | 34c19dd | Pal Sambit
**Subject:** `moved README out of src`
This was a pure file move that renamed `src/aruco_cube_gen/README.md` back to the repository-root `README.md` without content changes. Operational behavior did not change.

## 2025-12-24T14:12:18+08:00 | 98cc7d9 | Pal Sambit
**Subject:** `remove plate bezel and relocate ID text onto mitered plug face`
This removed the remaining bezel/flange from the actual plate geometry by zeroing its defaults and returning a plain tapered plug, then relocated the optional ID text onto the plug face inside the quiet zone with a slight embed to avoid coplanar-surface issues. On the cube side, the single perimeter support ring was replaced by four additive 45° ramps below the top slot floor, the default plate IDs changed from `0-4` to `5-9`, and the README was updated to describe pure mitered plugs with no decorative overhangs.

## 2026-03-13T10:40:24+08:00 | 5f4551e | Codex Agent
**Subject:** `Restructure the repository for multi-target calibration generation`
This expanded the repository from a cube-only generator into a target-oriented framework by adding `src/calibration_target_gen` with a generic CLI, target registry, base target protocol, artifact typing, output formatting, and manifest writing. The existing cube generator was wrapped as a registered `cube` target without removing the legacy entry point, and the documentation was split so the top-level README described the repository at workcell-target scope while cube-specific usage and extension guidance moved into new files under `docs/targets/` and `docs/development/`.

## 2026-03-13T10:46:29+08:00 | a735b15 | Codex Agent
**Subject:** `Add render images to the ArUco cube target guide`
This was a docs-only change that embedded the existing cube and cube-face plate render images into `docs/targets/aruco-cube.md` so the cube target guide showed the generated parts visually.

## 2026-03-16T15:31:19+08:00 | a07a21e | Codex
**Subject:** `Add rectangular ArUco plate target`
This added a new registered `aruco_plate` target under `src/calibration_target_gen/targets/aruco_plate/` with its own config, marker-layout math, STL geometry builders, flat preview generation, run-info writer, adapter, and registry entry. Operationally the repository could now generate a standalone `83 x 220 x 4 mm` single-marker plate as separate white and black STL bodies plus a preview PNG, and the README/docs were updated to expose that new target.

## 2026-03-16T15:34:16+08:00 | 9abee29 | Codex
**Subject:** `Add ChArUco plate target`
This added a new registered `charuco_plate` target with its own config, ChArUco board-layout logic, STL geometry builders, flat preview generation, run-info writer, adapter, and docs, plus a committed render image referenced by the guide. The implementation builds a `220 mm` square `3 x 3` board with separate white and black bodies, and the target-extension docs were updated to include the new folder layout.

## 2026-03-16T15:53:48+08:00 | 0bf4870 | Codex
**Subject:** `Add rendered previews for all targets`
This introduced shared shaded preview rendering in `src/calibration_target_gen/shared/render.py` and added `Pillow` to `requirements.txt`. The cube generator began writing `cube_render.png` and a representative `plate_render.png`, the standalone ArUco and ChArUco plate targets gained `*_render.png` outputs alongside their flat previews, `run_info.txt` started listing preview artifacts, and the target guides were updated to document the new rendered outputs.

## 2026-03-16T16:00:12+08:00 | 8832407 | Codex
**Subject:** `Add dedicated ArUco plate render image`
This was a docs-and-image update that added a dedicated committed render asset for the standalone ArUco plate and switched `docs/targets/aruco-plate.md` to display it. At the same time, the cube guide renamed its existing plate render caption so it was clear that image depicted a cube face plate rather than the standalone rectangular target.

## 2026-03-16T16:22:08+08:00 | c35566e | Codex
**Subject:** `Improve plate render readability`
This changed plate rendering from generic STL shading to a plate-specific compositing path that projects the flat preview image onto a perspectivized plate with side faces, outline strokes, and a blurred shadow. The ArUco and ChArUco generators now build `*_render.png` from the preview bitmap plus plate dimensions instead of from a simple mesh-pair render, which made the marker pattern easier to read in the generated and committed images.

## 2026-03-17T16:05:27+08:00 | d3cecec | Codex
**Subject:** `Add printable A4 ArUco sheet target`
This added a new registered `aruco_a4_sheet` target that writes multi-page PDFs of centered `150 mm` ArUco markers on A4 pages with a `10 mm` alignment grid, plus `run_info.txt` and a manifest. It also extracted shared marker-rectangle generation into `src/calibration_target_gen/shared/aruco.py`, and both the standalone plate and ChArUco board builders were refactored to reuse that shared ArUco logic instead of duplicating marker-image generation code.
