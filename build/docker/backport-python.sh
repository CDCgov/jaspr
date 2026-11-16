#!/bin/sh
set -eu

# Match the CPython source revision used by the pinned Chainguard images.
SOURCE_REVISION=64b5cfdf7548a21741398ce0826728818327aea7
# Official HTTP framing fix and its whitespace correction.
HTTP_FIX=2eb2af805c156ca52b316bb4ced5e0ab3971d0ae
HTTP_WHITESPACE_FIX=9f52b443c002cccfb54bda0706a9276b6b4a109d

git init /src/cpython
cd /src/cpython
git remote add origin https://github.com/python/cpython
git fetch --depth=2 origin \
    "$SOURCE_REVISION" "$HTTP_FIX" "$HTTP_WHITESPACE_FIX"
git checkout --detach "$SOURCE_REVISION"
git cherry-pick --no-commit "$HTTP_FIX" "$HTTP_WHITESPACE_FIX"

# Copy the patched source into both the builder and the runtime.
mkdir -p /patched/lib/python3.15/http
cp Lib/http/client.py /patched/lib/python3.15/http/client.py
cp /patched/lib/python3.15/http/client.py /usr/lib/python3.15/http/client.py
# The base image ships unchecked-hash bytecode, which otherwise masks this fix.
rm -f /usr/lib/python3.15/http/__pycache__/client.cpython-315.pyc \
    /usr/lib/python3.15/http/__pycache__/client.cpython-315.opt-1.pyc \
    /usr/lib/python3.15/http/__pycache__/client.cpython-315.opt-2.pyc
