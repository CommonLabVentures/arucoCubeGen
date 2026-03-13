# ArUco Cube Design Notes

This document captures the printability decisions behind the current ArUco cube target.

## Design Goals

- Reliable FDM printing
- Predictable slicer behavior
- No sudden unsupported geometry
- Consistent plate seating across faces

## Open Top Strategy

The top face uses the same slot geometry as the side faces, but the flat slot floor is removed so the top is open while the mitered seating walls remain intact.

This avoids internal roof geometry and removes cases where the slicer would need to start unsupported extrusion in the cube interior.

## Slot Seating Strategy

All slotted faces use the same geometry:

- Same slot size
- Same slot depth
- Same mitered wall profile

The plate seats on the mitered walls rather than on flat ledges.

## Internal Support Ramp

The cube adds a continuous internal 45 degree perimeter ramp below the top slot floor.

That ramp:

- Starts from the inner vertical walls
- Grows upward gradually
- Meets the inner edge of the top opening
- Adds material only below the slot floor plane

The point of the ramp is printability, not alignment.

## Plate Design

The matching plate is a tapered plug with no flange. This keeps the mating geometry simple and avoids floating overhangs on the part itself.

Optional ID text is embedded slightly into the plate face so slicers do not discard it as coplanar geometry.

## Detection Context

The target was sized around use with an Intel RealSense D455 RGB camera, with enough marker scale margin for detection around 1.5 meters.

## Lessons Learned

Rejected approaches:

- Flat internal roofs
- Long bridges
- Attic-style internal roofs
- Corbels and stepped partial supports

What held up:

- Miter-only seating
- Continuous additive support below the top opening
- Designing for layer-to-layer continuity instead of static shape alone

## Guiding Principle

If a feature appears suddenly at one layer, it is likely to fail. If it grows gradually from supported material, slicers behave much more predictably.
