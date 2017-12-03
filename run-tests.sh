#!/bin/bash

set -ue
set -o pipefail

for i in tests/*.maxe; do
    python3 -m maxe "$i" >/dev/null 2>&1 && echo "[ok] $i"
done
