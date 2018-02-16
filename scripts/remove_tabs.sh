#! /bin/bash
set -euo pipefail
IFS=$'\n\t'

sed -i -e 's/\t/    /g' `find ponder tests -name '*.py'`
