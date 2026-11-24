#!/usr/bin/env python3
"""The Houseplant Out-of-Office — make.fun bounty entry.

Writes one out-of-office auto-reply, at most 120 characters, as if a
houseplant had written it, to /output/entry.txt and prints it to stdout.

The entry line is fixed and deterministic: the same line every run.
"""

import hashlib
import os
import sys

ENTRY = (
    "I'm out of office \u2014 the fern filed for neglect, "
    "the cactus unionized, and the monstera is holding the window hostage."
)

MAX_CHARS = 120
OUTPUT_PATH = "/output/entry.txt"


def validate_entry(text: str) -> None:
    """Validate the entry line against the competition rules."""
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not text.strip():
        raise ValueError("entry must not be empty")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if len(text) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(text)} chars, over the {MAX_CHARS}-char limit"
        )
    for ch in text:
        code = ord(ch)
        if code < 0x20 or code == 0x7F:
            raise ValueError(f"entry contains control character U+{code:04X}")
        if code == 0xFFFD:
            raise ValueError("entry contains replacement character U+FFFD")
        if 0xD800 <= code <= 0xDFFF:
            raise ValueError(f"entry contains lone surrogate U+{code:04X}")
    # Must round-trip cleanly through UTF-8 with no loss or substitution.
    if text.encode("utf-8").decode("utf-8") != text:
        raise ValueError("entry does not round-trip through UTF-8")


def main() -> int:
    validate_entry(ENTRY)
    digest = hashlib.sha256(ENTRY.encode("utf-8")).hexdigest()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(ENTRY + "\n")
    # Read back and verify the written file is byte-identical to the entry.
    with open(OUTPUT_PATH, "r", encoding="utf-8", newline="") as fh:
        written = fh.read()
    if written != ENTRY + "\n":
        raise RuntimeError("read-back mismatch: /output/entry.txt differs")
    read_back_digest = hashlib.sha256(
        written.rstrip("\n").encode("utf-8")
    ).hexdigest()
    if read_back_digest != digest:
        raise RuntimeError("read-back sha256 mismatch")
    sys.stdout.write(ENTRY + "\n")
    sys.stderr.write(
        f"entry: {len(ENTRY)} chars, sha256 {digest}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
