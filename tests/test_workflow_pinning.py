"""Exercise the policy's actual embedded scanner, not a test-only copy.

Run with: python3 -m unittest discover -s tests -v (requires PyYAML).
"""
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/required-pr-policy.yml'
SHA = '0123456789abcdef0123456789abcdef01234567'


class WorkflowPinningTests(unittest.TestCase):
    def scan(self, source, suffix='yml'):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        step = next(s for s in workflow['jobs']['policy']['steps']
                    if s['name'] == 'Verify workflow dependency pinning')
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / '.github/workflows'
            directory.mkdir(parents=True)
            (directory / ('candidate.' + suffix)).write_text(source)
            (Path(tmp) / 'yaml.py').write_text("raise RuntimeError('untrusted import')\n")
            return subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp,
                                  text=True, capture_output=True)

    def test_mutable_refs_rejected_in_valid_yaml_forms(self):
        sources = [
            'jobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n',
            'jobs:\n  build:\n    steps:\n      - name: Checkout\n        uses: actions/checkout@v4\n',
            'jobs: {build: {steps: [{"uses": "actions/checkout@v4"}]}}',
            "jobs:\n  build:\n    steps:\n    - 'uses': 'actions/checkout@v4' # comment\n",
            'jobs:\n  build:\n    steps:\n    - uses: >-\n        actions/checkout@v4\n',
            'jobs: {build: {uses: "org/repo/.github/workflows/build.yml@main"}}',
            'jobs:\n  build:\n    steps:\n    - &checkout {uses: actions/checkout@v4}\n    - *checkout\n',
        ]
        for source in sources:
            for suffix in ('yaml', 'yml'):
                with self.subTest(source=source, suffix=suffix):
                    result = self.scan(source, suffix)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('40-character commit SHA', result.stdout)

    def test_missing_ref_and_invalid_sha_rejected(self):
        for target in ('actions/checkout', 'actions/checkout@abc123',
                       'actions/checkout@' + 'a' * 41, 'actions/checkout@' + 'A' * 40):
            with self.subTest(target=target):
                result = self.scan(yaml.safe_dump({'jobs': {'build': {'steps': [{'uses': target}]}}}))
                self.assertNotEqual(result.returncode, 0)

    def test_pins_local_and_docker_exceptions_accepted(self):
        for target in ('actions/checkout@' + SHA, './actions/local', 'docker://alpine:3'):
            with self.subTest(target=target):
                result = self.scan(yaml.safe_dump({'jobs': {'build': {'steps': [{'uses': target}]}}}))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.scan('jobs: {call: {uses: "org/repo/.github/workflows/build.yml@' + SHA + '"}}')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shell_text_and_nested_input_named_uses_are_not_actions(self):
        source = 'jobs:\n  build:\n    steps:\n    - run: |\n        uses: mutable/text@main\n    - uses: ./.github/local\n      with:\n        uses: arbitrary-data\n'
        result = self.scan(source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_yaml_and_non_string_uses_fail_closed(self):
        for source in ('jobs: [', 'jobs: {build: {steps: [{uses: null}]}}',
                       'jobs: {build: {steps: [{uses: [actions/checkout]}]}}'):
            with self.subTest(source=source):
                self.assertNotEqual(self.scan(source).returncode, 0)


if __name__ == '__main__':
    unittest.main()
