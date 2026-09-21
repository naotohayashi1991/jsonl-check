import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonl_check import validate

SCRIPT = Path(__file__).resolve().parents[1] / "jsonl_check.py"


class ValidationTests(unittest.TestCase):
    def test_all_json_value_types_and_unicode(self):
        self.assertEqual(validate(io.StringIO('{}\n[]\n"日本語"\n42\ntrue\nnull\n')), (6, []))

    def test_invalid_lines(self):
        self.assertEqual(validate(io.StringIO('{}\n\n{bad}\nNaN\nInfinity\n-Infinity\n')), (6, [2, 3, 4, 5, 6]))

    def test_empty_file(self):
        self.assertEqual(validate(io.StringIO('')), (0, []))

    def test_crlf_and_no_final_newline(self):
        self.assertEqual(validate(io.StringIO('{}\r\n[]')), (2, []))

    def test_bom_rejected(self):
        self.assertEqual(validate(io.StringIO('\ufeff{}\n')), (1, [1]))

    def run_cli(self, data):
        return subprocess.run([sys.executable, str(SCRIPT), '-'], input=data, capture_output=True)

    def test_cli_valid(self):
        p = self.run_cli(b'{}\n')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {'lines': 1, 'invalid_lines': [], 'valid': True})

    def test_cli_does_not_echo_input(self):
        p = self.run_cli(b'sensitive-example-invalid\n')
        self.assertEqual(p.returncode, 1)
        self.assertNotIn(b'sensitive-example-invalid', p.stdout + p.stderr)

    def test_invalid_utf8(self):
        p = self.run_cli(b'\xff\n')
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout), {'error': 'input_read_failed'})

    def test_file_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.jsonl'
            path.write_text('{}\n', encoding='utf-8')
            p = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True)
            self.assertEqual(p.returncode, 0)
            path.unlink()
            p = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True)
            self.assertEqual(p.returncode, 2)
            self.assertNotIn(str(path).encode(), p.stdout + p.stderr)


if __name__ == '__main__':
    unittest.main()
