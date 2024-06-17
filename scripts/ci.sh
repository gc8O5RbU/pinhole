#!/bin/bash
set -e

cd $(dirname $(realpath $0))/..

pycodestyle . \
    --max-line-length 120

mypy pinhole