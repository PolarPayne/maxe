#!/bin/bash

set -xue
set -o pipefail

for i in tests/*.maxe; do
    python3 -m maxe $i
done
