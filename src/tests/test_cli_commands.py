import subprocess
import sys


def test_leaderboard_help():
    result = subprocess.run([sys.executable, 'leaderboard.py', '-h'], capture_output=True, text=True, cwd='src')
    assert result.returncode == 0
    assert 'usage' in result.stdout


def test_submit_help():
    result = subprocess.run([sys.executable, 'submit.py', '-h'], capture_output=True, text=True, cwd='src')
    assert result.returncode == 0
    assert 'usage' in result.stdout
