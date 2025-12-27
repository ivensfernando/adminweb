#!/bin/bash

set -o errexit
set -o pipefail


if [ -z "${SERVER_ROLE}" ]; then
  exec "$@"
else
  scripts/start.sh
fi
