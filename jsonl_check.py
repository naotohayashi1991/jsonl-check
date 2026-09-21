#!/usr/bin/env python3
"""Validate JSON Lines without printing input contents; standard library only."""
import argparse
import json
import sys


def reject_constant(value):
    raise ValueError("non-standard JSON constant")


def validate(stream):
    """Return (record count, invalid line numbers); blank lines are invalid."""
    count = 0
    invalid = []
    for number, line in enumerate(stream, 1):
        try:
            json.loads(line, parse_constant=reject_constant)
        except (ValueError, RecursionError):
            invalid.append(number)
        count += 1
    return count, invalid


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="UTF-8 JSONL file, or - for UTF-8 stdin")
    args = parser.parse_args(argv)
    try:
        if args.file == "-":
            import io
            stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="strict")
            count, invalid = validate(stream)
        else:
            with open(args.file, encoding="utf-8", errors="strict") as stream:
                count, invalid = validate(stream)
    except (OSError, UnicodeError):
        print(json.dumps({"error": "input_read_failed"}))
        return 2
    print(json.dumps({"lines": count, "invalid_lines": invalid, "valid": not invalid}))
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
