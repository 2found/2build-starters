#!/usr/bin/env python3
"""Exercise publication guards with real Git tags and a local release-service fake."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/release.sh'

FAKE_GH = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
state_file = Path(os.environ['RELEASE_TEST_STATE'])
state = json.loads(state_file.read_text())
with state_file.with_suffix('.calls').open('a') as log:
    log.write(json.dumps(sys.argv[1:]) + '\\n')
if sys.argv[1:3] == ['release', 'view']:
    if state['mode'] == 'missing':
        print('release not found', file=sys.stderr); sys.exit(1)
    if state['mode'] == 'error':
        print('HTTP 403: forbidden', file=sys.stderr); sys.exit(1)
    print(json.dumps({'isDraft': state['mode'] == 'draft',
                      'isPrerelease': state['mode'] == 'prerelease'}))
elif sys.argv[1:3] == ['release', 'create']:
    if state.get('create_error'):
        print('HTTP 503: unavailable', file=sys.stderr); sys.exit(1)
    state['mode'] = 'stable'; state_file.write_text(json.dumps(state))
else:
    sys.exit(2)
'''


class ReleasePolicy(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='starter-release-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.remote = self.root / 'origin.git'
        self.env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
                    'GIT_AUTHOR_NAME': 'release-test', 'GIT_AUTHOR_EMAIL': 'release@test.invalid',
                    'GIT_COMMITTER_NAME': 'release-test', 'GIT_COMMITTER_EMAIL': 'release@test.invalid',
                    'GITHUB_REF': 'refs/heads/main'}
        self.git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'main')
        self.git('remote', 'add', 'origin', str(self.remote))
        (self.repo / 'catalog.json').write_text(json.dumps({'version': '0.1.0'}))
        self.git('add', 'catalog.json')
        self.git('commit', '-m', 'initial starter')
        self.sha = self.git('rev-parse', 'HEAD').stdout.strip()
        self.env['GITHUB_SHA'] = self.sha
        self.git('push', '-u', 'origin', 'main')
        binaries = self.root / 'bin'
        binaries.mkdir()
        fake = binaries / 'gh'
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        self.env['PATH'] = str(binaries) + os.pathsep + self.env['PATH']
        self.state = self.root / 'release.json'
        self.env['RELEASE_TEST_STATE'] = str(self.state)
        self.set_release('missing')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, env=self.env,
                              text=True, capture_output=True, check=True)

    def set_release(self, mode, **options):
        self.state.write_text(json.dumps({'mode': mode, **options}))

    def release(self, success=True):
        result = subprocess.run(['bash', str(SCRIPT)], cwd=self.repo, env=self.env,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def remote_tags(self):
        return self.git('ls-remote', '--tags', 'origin').stdout

    def created(self):
        calls = self.state.with_suffix('.calls')
        return calls.exists() and any(json.loads(line)[:2] == ['release', 'create']
                                      for line in calls.read_text().splitlines())

    def test_verified_main_creates_stable_release_and_pinned_tag(self):
        self.release()
        self.assertIn(self.sha, self.remote_tags())
        self.assertIn('refs/tags/v0.1.0^{}', self.remote_tags())
        self.assertTrue(self.created())
        self.assertEqual(json.loads(self.state.read_text())['mode'], 'stable')

    def test_same_version_push_does_not_move_published_tag(self):
        self.release()
        tags = self.remote_tags()
        (self.repo / 'README.md').write_text('Documentation change')
        self.git('add', 'README.md')
        self.git('commit', '-m', 'docs')
        self.env['GITHUB_SHA'] = self.git('rev-parse', 'HEAD').stdout.strip()
        self.release()
        self.assertEqual(self.remote_tags(), tags)

    def test_publication_retry_uses_existing_verified_tag(self):
        self.set_release('missing', create_error=True)
        self.release(success=False)
        tags = self.remote_tags()
        self.assertIn(self.sha, tags)
        self.set_release('missing')
        self.release()
        self.assertEqual(self.remote_tags(), tags)

    def test_tag_at_other_commit_is_rejected(self):
        self.git('tag', 'v0.1.0')
        self.git('commit', '--allow-empty', '-m', 'new untagged commit')
        self.env['GITHUB_SHA'] = self.git('rev-parse', 'HEAD').stdout.strip()
        self.release(success=False)
        self.assertFalse(self.remote_tags())
        self.assertFalse(self.created())

    def test_service_failure_does_not_create_tag(self):
        self.set_release('error')
        self.release(success=False)
        self.assertFalse(self.remote_tags())
        self.assertFalse(self.created())

    def test_nonstable_existing_releases_are_rejected(self):
        for mode in ['draft', 'prerelease']:
            with self.subTest(mode=mode):
                self.set_release(mode)
                self.release(success=False)
                self.assertFalse(self.remote_tags())
                self.assertFalse(self.created())

    def test_unverified_commit_or_wrong_ref_cannot_publish(self):
        for field, value in [('GITHUB_SHA', '0' * 40),
                             ('GITHUB_REF', 'refs/heads/feature'),
                             ('GITHUB_REF', 'refs/tags/v0.2.0')]:
            with self.subTest(field=field, value=value):
                previous = self.env[field]
                self.env[field] = value
                self.release(success=False)
                self.env[field] = previous
                self.assertFalse(self.remote_tags())
                self.assertFalse(self.created())

    def test_manual_matching_tag_is_supported(self):
        self.git('tag', 'v0.1.0')
        self.env['GITHUB_REF'] = 'refs/tags/v0.1.0'
        self.release()
        self.assertIn(self.sha, self.remote_tags())
        self.assertTrue(self.created())

    def test_invalid_catalog_version_cannot_publish(self):
        for version in ['0.1.0-beta.1', '../main', '01.1.0']:
            with self.subTest(version=version):
                (self.repo / 'catalog.json').write_text(json.dumps({'version': version}))
                self.release(success=False)
                self.assertFalse(self.remote_tags())
                self.assertFalse(self.created())


if __name__ == '__main__':
    unittest.main(verbosity=2)
