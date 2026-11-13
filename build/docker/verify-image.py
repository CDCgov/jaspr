"""Verify image security fixes and the applicability of remaining CPE matches."""

import argparse
import http.client
import importlib.util
from io import BytesIO
import locale
import os
from pathlib import Path
import shutil
import socket
import sys
from xml.parsers import expat


class MemorySocket:
    def __init__(self, data):
        self.data = data

    def makefile(self, mode):
        return BytesIO(self.data)


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--launch", action="store_true", help="Start JASPR after verification")
    options = arguments.parse_args()

    if expat.version_info < (2, 10, 0):
        raise SystemExit(
            f"Vulnerable XML parser: {expat.EXPAT_VERSION}; require Expat >= 2.10.0"
        )

    for package in ("pip", "setuptools", "wheel"):
        if importlib.util.find_spec(package) is not None:
            raise SystemExit(f"Build-only package present in runtime: {package}")
    if list(Path("/usr/share/python-wheels").glob("*.whl")):
        raise SystemExit("Build-only bootstrap wheels present in runtime")

    parser = expat.ParserCreate()
    parser.Parse("<root><item>ok</item></root>", True)

    for host, port in (
        ("127.0.0.1\0.example", 80),
        (b"127.0.0.1\0.example", 80),
        ("127.0.0.1", "80\0suffix"),
        ("127.0.0.1", b"80\0suffix"),
    ):
        try:
            socket.getaddrinfo(host, port)
        except ValueError:
            pass
        else:
            raise SystemExit("CVE-2026-116566: getaddrinfo accepted a null byte")

    for chunk_size in (b"-1", b"+1", b"0x1", b"1_0"):
        response = http.client.HTTPResponse(
            MemorySocket(
                b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n"
                + chunk_size
                + b"\r\n"
            )
        )
        response.begin()
        try:
            response._read_next_chunk_size()
        except ValueError:
            pass
        else:
            raise SystemExit("CVE-2026-103995: HTTP parser accepted invalid framing")
        finally:
            response.close()

            response = http.client.HTTPResponse(
                MemorySocket(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\nok\r\n0\r\n\r\n")
            )
            response.begin()
            if response.read() != b"ok":
                raise SystemExit("HTTP chunked response compatibility regression")
            response.close()

    for length in (b"+1", b"1_0", b"-1"):
        response = http.client.HTTPResponse(
            MemorySocket(b"HTTP/1.1 200 OK\r\nContent-Length: " + length + b"\r\n\r\n")
        )
        response.begin()
        if response.length is not None:
            raise SystemExit("CVE-2026-103995: HTTP parser accepted invalid length")
        response.close()

    response = http.client.HTTPResponse(
        MemorySocket(b"HTTP/1.1 200 OK\r\nContent-Length: 2 \t\r\n\r\nok")
    )
    response.begin()
    if response.read() != b"ok":
        raise SystemExit("HTTP Content-Length whitespace compatibility regression")
    response.close()

    socket.getaddrinfo("127.0.0.1", 80, flags=socket.AI_NUMERICHOST)

    # CVE-2026-84243 requires gettext to use a non-C messages locale.
    if locale.setlocale(locale.LC_MESSAGES, "") not in ("C.UTF-8", "C.utf8", "C", "POSIX"):
        raise SystemExit("Reassess CVE-2026-84243: non-C message locale enabled")
    if set(Path("/usr/lib/locale").iterdir()) != {Path("/usr/lib/locale/C.utf8")}:
        raise SystemExit("Reassess CVE-2026-84243: additional locales installed")
    # CVE-2026-119586 affects the SQLite shell's .recover command, not sqlite-libs.
    if shutil.which("sqlite3") is not None:
        raise SystemExit("Reassess CVE-2026-119586: SQLite command-line shell installed")

    print(f"Runtime checks passed: Python {sys.version.split()[0]}, {expat.EXPAT_VERSION}")
    if options.launch:
        os.execv(
            "/usr/bin/tini",
            ["/usr/bin/tini", "--", "/opt/venv/bin/uwsgi", "--ini", "/app/app.ini"],
        )


if __name__ == "__main__":
    main()
