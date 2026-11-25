#!/usr/bin/env python3
"""
Room Storage Spec Deterministic Engineering Auditor
Checks wall bounds, door-swing clearance, pairwise AABB overlaps,
under-bed drawer slide clearance, pet safety height, and GB 50096 walkways.
"""

import json
import math
import sys


def item_aabb(cx, cz, w, d, rot_y=0.0):
    """Return 2D XZ bounding box (minx, maxx, minz, maxz) rotated around Y."""
    c = abs(math.cos(rot_y))
    s = abs(math.sin(rot_y))
    hx = (w * 0.5) * c + (d * 0.5) * s
    hz = (d * 0.5) * c + (w * 0.5) * s
    return (cx - hx, cx + hx, cz - hz, cz + hz)


def boxes_overlap(a, b, tol=0.015):
    """Check if two XZ boxes intersect beyond tolerance (in meters)."""
    return (
        (a[0] + tol < b[1] and a[1] - tol > b[0])
        and (a[2] + tol < b[3] and a[3] - tol > b[2])
    )


def get_door_sweep_box(room_w, room_d, door):
    """Return conservative inward clearance box for the door swing zone."""
    dw = float(door.get("width", 0.90))
    off = float(door.get("offset", -1.65))
    wall = door.get("wall", "west")
    hw = room_w * 0.5
    hd = room_d * 0.5
    inner_x = hw - 0.08
    inner_z = hd - 0.08

    if wall == "west":
        return (-inner_x, -inner_x + dw, off - dw * 0.5, off + dw * 0.5)
    if wall == "east":
        return (inner_x - dw, inner_x, off - dw * 0.5, off + dw * 0.5)
    if wall == "north":
        return (off - dw * 0.5, off + dw * 0.5, -inner_z, -inner_z + dw)
    return (off - dw * 0.5, off + dw * 0.5, inner_z - dw, inner_z)


def audit_spec(spec):
    """Run all spatial, collision, and ergonomic checks on a room_spec dict."""
    errors = []
    warnings = []
    info = []

    room = spec["room"]
    rw = float(room["width"])
    rd = float(room["depth"])
    rh = float(room.get("height", 2.6))
    wall_t = 0.08
    inner_bounds = (-rw * 0.5 + wall_t, rw * 0.5 - wall_t, -rd * 0.5 + wall_t, rd * 0.5 - wall_t)

    door = spec["door"]
    door_box = get_door_sweep_box(rw, rd, door)

    bed = spec["bed"]
    bed_box = item_aabb(bed["x"], bed["z"], bed["width"], bed["length"], bed.get("rotY", 0))

    furn = spec.get("furniture", {})
    desk = furn["desk"]
    desk_box = item_aabb(desk["x"], desk["z"], desk["width"], desk["depth"], desk.get("rotY", 0))

    chair = furn["chair"]
    chair_box = item_aabb(chair["x"], chair["z"], 0.48, 0.48, chair.get("rotY", 0))

    wardrobe = furn["wardrobe"]
    wardrobe_box = item_aabb(wardrobe["x"], wardrobe["z"], wardrobe["width"], wardrobe["length"], wardrobe.get("rotY", 0))

    cat = furn.get("catStation")
    cat_box = item_aabb(cat["x"], cat["z"], 0.34, 1.36, cat.get("rotY", 0)) if cat else None

    racket = furn.get("racketMount")
    racket_box = item_aabb(racket["x"], racket["z"], 0.16, 0.56, racket.get("rotY", 0)) if racket else None

    solids = [
        ("bed", bed_box),
        ("desk", desk_box),
        ("chair", chair_box),
        ("wardrobe", wardrobe_box),
    ]
    if cat_box:
        solids.append(("catStation", cat_box))

    # 1. Wall-bounds verification
    for name, b in solids:
        if (
            b[0] < inner_bounds[0] - 0.01
            or b[1] > inner_bounds[1] + 0.01
            or b[2] < inner_bounds[2] - 0.01
            or b[3] > inner_bounds[3] + 0.01
        ):
            errors.append(f"[WALL_OUT] '{name}' box {tuple(round(x, 3) for x in b)} exceeds inner walls {tuple(round(x, 3) for x in inner_bounds)}")

    # 2. Door swing clearance check
    for name, b in solids:
        if boxes_overlap(b, door_box, tol=0.02):
            errors.append(f"[DOOR_BLOCK] '{name}' collides with door swing zone {tuple(round(x, 3) for x in door_box)}")

    # 3. Pairwise solid object intersection checks
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            n1, b1 = solids[i]
            n2, b2 = solids[j]
            # Allow ergonomic chair tucked up to 15cm under desk front
            tol = 0.16 if {n1, n2} == {"desk", "chair"} else 0.015
            if boxes_overlap(b1, b2, tol=tol):
                errors.append(f"[OVERLAP] '{n1}' overlaps with '{n2}'")

    # 4. Under-bed drawer vertical clearance & pull-out path check
    bed_clear = float(bed.get("clearance", 0.22))
    drawer_h = float(bed.get("underDrawerHeight", 0.188))
    if bed_clear - drawer_h < 0.018:
        errors.append(f"[CLEARANCE] Under-bed drawer height ({drawer_h:.3f}m) leaves < 1.8cm gap under bed ({bed_clear:.3f}m)")
    else:
        info.append(f"[OK] Under-bed vertical clearance margin: {(bed_clear - drawer_h) * 100:.1f} cm")

    slide = float(bed.get("underDrawerSlide", 0.55))
    slide_side = bed.get("underDrawerSide", "west")
    if slide > 0:
        if slide_side == "west":
            drawer_pull_box = (bed_box[0] - slide, bed_box[0], bed_box[2] + 0.12, bed_box[3] - 0.05)
        else:
            drawer_pull_box = (bed_box[1], bed_box[1] + slide, bed_box[2] + 0.12, bed_box[3] - 0.05)
        for name, b in solids:
            if name == "bed":
                continue
            if boxes_overlap(drawer_pull_box, b, tol=0.02):
                errors.append(f"[DRAWER_CLASH] Under-bed pulled drawer path collides with '{name}'")

    # 5. Cat / Pet Safety Height Check
    if spec.get("meta", {}).get("petFriendly", True) and racket:
        hook_y = float(racket.get("hookY", 1.80))
        if hook_y < 1.70:
            errors.append(f"[PET_SAFETY] Racket wall hook ({hook_y:.2f}m) is below 1.70m cat jump zone")
        else:
            info.append(f"[OK] Racket hook safe above cat jump height: {hook_y:.2f}m")

    # 6. GB 50096 Main Walkway Check (Gap between West furniture & East furniture in main corridor)
    if wardrobe_box[0] > desk_box[1]:
        aisle_w = wardrobe_box[0] - desk_box[1]
        info.append(f"[OK] Main aisle clear width (desk <-> wardrobe): {aisle_w * 100:.1f} cm")
        if aisle_w < 0.60:
            errors.append(f"[WALKWAY] Main aisle width {aisle_w * 100:.1f}cm < 60cm mandatory minimum")
        elif aisle_w < 0.85:
            warnings.append(f"[WALKWAY_TIGHT] Main aisle {aisle_w * 100:.1f}cm < 85cm comfortable target")

    if wardrobe_box[2] > bed_box[3]:
        bed_gap = wardrobe_box[2] - bed_box[3]
        info.append(f"[OK] Bed-foot to wardrobe passage: {bed_gap * 100:.1f} cm")
        if bed_gap < 0.35:
            warnings.append(f"[BED_GAP_TIGHT] Bed-foot clearance {bed_gap * 100:.1f}cm < 35cm")

    return errors, warnings, info


def main():
    if len(sys.argv) < 2:
        print("Usage: audit_room_spec.py <room_spec.json>")
        sys.exit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        spec = json.load(f)

    errors, warnings, info = audit_spec(spec)
    print(f"=== Room Spec Audit: {spec.get('meta', {}).get('title', sys.argv[1])} ===")
    for line in info:
        print(" ", line)
    for line in warnings:
        print("  [WARN]", line)
    for line in errors:
        print("  [FAIL]", line)

    if errors:
        print(f"\nRESULT: FAILED ({len(errors)} blocking spatial/physics errors)")
        sys.exit(1)
    print(f"\nRESULT: PASSED (0 blocking errors, {len(warnings)} warnings)")
    sys.exit(0)


if __name__ == "__main__":
    main()
