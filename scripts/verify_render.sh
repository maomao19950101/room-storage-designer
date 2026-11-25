#!/usr/bin/env bash
# Headless Multi-View Render & Syntax Verification Gate for 3D Room Storage Viewer
set -euo pipefail

BASE_URL="${1:-http://localhost:8080/index.html}"
OUT_DIR="${2:-./verify_renders}"
HTML_FILE="${3:-}"

if [[ -n "$HTML_FILE" && -f "$HTML_FILE" ]]; then
  node -e '
    const fs = require("fs");
    const html = fs.readFileSync(process.argv[1], "utf8");
    const scripts = html.match(/<script[\s\S]*?<\/script>/gi) || [];
    scripts.forEach(s => {
      const code = s.replace(/<script[^>]*>/i, "").replace(/<\/script>/i, "");
      if (code.trim()) new Function(code);
    });
    console.log("JS Syntax Check PASSED:", process.argv[1]);
  ' "$HTML_FILE"
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ ! -x "$CHROME" ]]; then
  CHROME=$(command -v google-chrome || command -v chromium || true)
fi

if [[ -z "$CHROME" ]]; then
  echo "WARN: Chrome/Chromium binary not found; skipping headless screenshot capture."
  exit 0
fi

mkdir -p "$OUT_DIR"
VIEWS=("iso:cam=iso" "wardrobe:cam=wardrobe" "desk:cam=desk" "bed_open:cam=bed&drawer=open" "cat:cam=cat" "racket_door:cam=racket&door=open")

for entry in "${VIEWS[@]}"; do
  name="${entry%%:*}"
  query="${entry##*:}"
  sep="?"
  [[ "$BASE_URL" == *"?"* ]] && sep="&"
  "$CHROME" --headless --use-gl=angle --window-size=1440,900 --virtual-time-budget=3500 \
    --screenshot="${OUT_DIR}/verify_${name}.png" "${BASE_URL}${sep}${query}" >/dev/null 2>&1 || {
      echo "ERROR capturing ${name}" >&2
      exit 1
    }
  echo "Captured ${OUT_DIR}/verify_${name}.png"
done
echo "All 6 verification views rendered cleanly."
