#!/usr/bin/env python3
"""
Build Parameterized 1:1 3D Room Storage Viewer from a declarative room_spec.json.
Runs audit_room_spec.py first unless --force is passed.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Build 3D Room Viewer from room_spec.json")
    parser.add_argument("spec_path", help="Path to room_spec.json")
    parser.add_argument("out_dir", help="Target output directory for index.html and libs/")
    parser.add_argument("--filename", default="index.html", help="Output HTML filename")
    parser.add_argument("--force", action="store_true", help="Skip audit failure abort")
    args = parser.parse_args()

    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audit_script = os.path.join(skill_root, "scripts", "audit_room_spec.py")
    tpl_html = os.path.join(skill_root, "templates", "3d_room_viewer.html")
    tpl_libs = os.path.join(skill_root, "templates", "libs")

    if not args.force:
        res = subprocess.run([sys.executable, audit_script, args.spec_path], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(res.stderr, file=sys.stderr)
            print("ERROR: Room spec failed engineering audit. Fix errors or pass --force.", file=sys.stderr)
            sys.exit(res.returncode)

    with open(args.spec_path, "r", encoding="utf-8") as f:
        spec_obj = json.load(f)

    with open(tpl_html, "r", encoding="utf-8") as f:
        html = f.read()

    marker = "/*__ROOM_SPEC_INJECT__*/"
    if marker not in html:
        print(f"ERROR: Marker {marker} missing in template {tpl_html}", file=sys.stderr)
        sys.exit(1)

    injected = html.replace(marker, f"window.ROOM_SPEC = {json.dumps(spec_obj, ensure_ascii=False, indent=2)};")

    os.makedirs(args.out_dir, exist_ok=True)
    out_html_path = os.path.join(args.out_dir, args.filename)
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(injected)

    dst_libs = os.path.join(args.out_dir, "libs")
    if os.path.exists(tpl_libs):
        os.makedirs(dst_libs, exist_ok=True)
        for fn in os.listdir(tpl_libs):
            src_f = os.path.join(tpl_libs, fn)
            if os.path.isfile(src_f):
                shutil.copy2(src_f, os.path.join(dst_libs, fn))

    print(f"Built parameterized 3D Room Viewer -> {out_html_path} ({len(injected)} bytes)")


if __name__ == "__main__":
    main()
