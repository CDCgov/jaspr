#!/bin/sh
set -eu

# Match the CPython source revision used by the pinned Chainguard images.
SOURCE_REVISION=4af98bdb94beb37453a33b989f8ef466f8ef0e21
# Official 3.15 socket backport, HTTP framing fix, and its whitespace correction.
SOCKET_FIX=85736acae75467a6ec565f6b609147e8ae8655fc
HTTP_FIX=2eb2af805c156ca52b316bb4ced5e0ab3971d0ae
HTTP_WHITESPACE_FIX=9f52b443c002cccfb54bda0706a9276b6b4a109d

git init /src/cpython
cd /src/cpython
git remote add origin https://github.com/python/cpython
git fetch --depth=2 origin \
    "$SOURCE_REVISION" "$SOCKET_FIX" "$HTTP_FIX" "$HTTP_WHITESPACE_FIX"
git checkout --detach "$SOURCE_REVISION"
git cherry-pick --no-commit "$SOCKET_FIX" "$HTTP_FIX" "$HTTP_WHITESPACE_FIX"

# Only these two modules change; use the installed interpreter's ABI and headers.
mkdir -p /patched/lib/python3.15/lib-dynload /patched/lib/python3.15/http
gcc -shared -fPIC -DPy_BUILD_CORE_MODULE \
    $(python3-config --cflags) \
    -I/usr/include/python3.15/internal \
    Modules/socketmodule.c \
    $(python3-config --ldflags) \
    -o "/patched/lib/python3.15/lib-dynload/_socket$(python3-config --extension-suffix)"
cp Lib/http/client.py /patched/lib/python3.15/http/client.py
cp /patched/lib/python3.15/lib-dynload/_socket*.so /usr/lib/python3.15/lib-dynload/
cp /patched/lib/python3.15/http/client.py /usr/lib/python3.15/http/client.py
# The base image ships unchecked-hash bytecode, which otherwise masks this fix.
rm -f /usr/lib/python3.15/http/__pycache__/client.cpython-315.pyc \
    /usr/lib/python3.15/http/__pycache__/client.cpython-315.opt-1.pyc \
    /usr/lib/python3.15/http/__pycache__/client.cpython-315.opt-2.pyc
