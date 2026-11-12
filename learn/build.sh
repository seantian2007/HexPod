#!/bin/bash
# Build the stage notebooks into the website, then serve it locally.
# Run from the code/ folder:  bash learn/build.sh
set -e
cd "$(dirname "$0")"
marimo export html-wasm notebooks/stage3_ik.py -o site/stage3/notebook --mode edit -f
echo ""
echo "Open http://localhost:8000/stage3/  (Ctrl+C to stop)"
python3 -m http.server 8000 --directory site
