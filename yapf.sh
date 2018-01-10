#!/usr/bin/env sh

set -ex

find . -name '*py' | xargs yapf -i
