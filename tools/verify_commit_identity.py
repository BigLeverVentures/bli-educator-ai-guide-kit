#!/usr/bin/env python3
"""Check reachable Git attribution without printing rejected contact addresses."""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile
import unittest


def allowed_email(value):
    """Accept GitHub's account and web-merge no-reply identities only."""
    return value == 'noreply@github.com' or bool(re.fullmatch(
        r'[A-Za-z0-9][A-Za-z0-9+._-]*@users\.noreply\.github\.com', value))


def attribution_errors(author, committer, message):
    errors = []
    for role, value in [('author', author), ('committer', committer)]:
        if not allowed_email(value):
            errors.append(role)
    for line in message.splitlines():
        if re.match(r'^\s*co-authored-by\s*:', line, re.I):
            match = re.fullmatch(r'\s*co-authored-by\s*:\s*[^<>\n]+<([^<>\n]+)>\s*', line, re.I)
            if not match or not allowed_email(match[1]):
                errors.append('co-author')
    return errors


def verify(root):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    commits = git('rev-list', '--all').splitlines()
    if not commits:
        raise ValueError('No reachable commits to verify')
    rejected = []
    for commit in commits:
        content = git('show', '-s', '--format=%ae%n%ce%n%B', commit)
        author, committer, *message = content.splitlines()
        errors = attribution_errors(author, committer, '\n'.join(message))
        if errors:
            rejected.append(commit + ': ' + ', '.join(sorted(set(errors))))
    if rejected:
        raise ValueError('Use GitHub no-reply attribution; rejected fields (addresses omitted):\n' + '\n'.join(rejected))
    return len(commits)


class IdentityTests(unittest.TestCase):
    account = '12345+educator@users.noreply.github.com'

    def test_allowed_and_rejected_addresses(self):
        for value in [self.account, 'educator@users.noreply.github.com', 'noreply@github.com']:
            self.assertTrue(allowed_email(value))
        for value in ['', 'educator@example.invalid', 'noreply@github.com.example.invalid',
                      'educator@users.noreply.github.com.example.invalid', 'Name <'+self.account+'>']:
            self.assertFalse(allowed_email(value))

    def test_all_attribution_fields_and_malformed_trailer(self):
        self.assertEqual(attribution_errors(self.account, 'noreply@github.com', 'Subject'), [])
        self.assertEqual(attribution_errors('author@example.invalid', 'committer@example.invalid',
            'Subject\n\nCo-authored-by: Partner <person@example.invalid>'), ['author', 'committer', 'co-author'])
        self.assertEqual(attribution_errors(self.account, self.account,
            'Subject\n\ncO-aUtHoReD-bY: Partner <'+self.account+'>'), [])
        self.assertEqual(attribution_errors(self.account, self.account, 'Co-authored-by: missing address'), ['co-author'])

    def test_history_and_non_main_refs_are_checked_without_echoing_email(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], stderr=subprocess.DEVNULL, text=True).strip()
            git('init', '-q', '-b', 'main')
            git('config', 'user.name', 'Fictional Educator')
            git('config', 'user.email', self.account)
            git('config', 'commit.gpgsign', 'false')
            git('config', 'core.hooksPath', '/dev/null')
            (root/'lesson.txt').write_text('Fictional lesson fixture\n')
            git('add', 'lesson.txt'); git('commit', '-qm', 'Publish teaching fixture')
            self.assertEqual(verify(root), 1)
            git('switch', '-qc', 'fixture-review')
            git('-c', 'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-qm', 'Synthetic rejected identity')
            git('switch', '-q', 'main')
            with self.assertRaises(ValueError) as error:
                verify(root)
            self.assertNotIn('fixture@example.invalid', str(error.exception))
            git('branch', '-D', 'fixture-review')
            git('commit', '--allow-empty', '-qm', 'Teaching fixture\n\nCo-authored-by: Fictional Partner <fixture@example.invalid>')
            with self.assertRaises(ValueError):
                verify(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=['verify_commit_identity'], exit=True)
    else:
        try:
            count = verify(Path(__file__).resolve().parents[1])
        except (ValueError, subprocess.CalledProcessError) as error:
            parser.exit(1, str(error) + '\n')
        print('No-reply attribution verified for ' + str(count) + ' reachable commits.')
