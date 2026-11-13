#!/bin/bash
# Build the practice notebooks into the website, then serve the whole site locally.
# Run from the code/ folder:  bash learn/build.sh
set -e
cd "$(dirname "$0")"
for nb in stage0:stage0_servo stage1:stage1_fk stage2:stage2_cal stage3:stage3_ik \
          stage4:stage4_jacobian stage5:stage5_body stage6:stage6_gait; do
  stage=${nb%%:*}; name=${nb#*:}
  marimo export html-wasm "notebooks/$name.py" -o "site/$stage/notebook" --mode edit -f
done
echo ""
echo "Open http://localhost:8000/  (Ctrl+C to stop)"
python3 -m http.server 8000 --directory site
