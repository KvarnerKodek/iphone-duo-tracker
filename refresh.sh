#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec python3 build.py --config "${1:-retailers.json}" --site "${SITE_DIR:-site}"
