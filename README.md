# jsonl-check

A small, dependency-free JSON Lines validator for Python 3.10+.
It reports invalid line numbers without printing file paths or input values.
No network requests or input-file writes are performed.

```sh
python3 jsonl_check.py events.jsonl
printf '{}\n[]\n' | python3 jsonl_check.py -
python3 -m unittest discover -s tests -v
```

Output: `{"lines": 2, "invalid_lines": [], "valid": true}`.
Exit status: 0 = valid; 1 = invalid JSON lines; 2 = read/UTF-8/usage error.
Read errors emit `{"error": "input_read_failed"}`; usage errors use argparse stderr.

Each line must contain one JSON value. Blank lines, a UTF-8 BOM, NaN and
Infinity are invalid. CRLF and a missing final newline are accepted.
An empty file is accepted. Scalars and duplicate object keys are accepted;
this checks JSON syntax, not an application schema or key uniqueness.
Read errors do not emit partial validation results.

The file is processed one line at a time, but a whole line and all invalid
line numbers are kept in memory. Use input-size limits for untrusted files;
this is not a resource-isolation or secret-scanning tool. Python's own
numeric and nesting limits apply.

## Contributing

Keep the runtime free of third-party dependencies. Include a regression test
for behavior changes and run the unittest command above before opening a PR.

## License

MIT; see LICENSE.
