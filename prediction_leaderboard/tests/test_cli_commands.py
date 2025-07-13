import subprocess
import sys


def test_leaderboard_help():
    result = subprocess.run([sys.executable, '-m', 'prediction_leaderboard.leaderboard', '-h'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage' in result.stdout


def test_submit_help():
    result = subprocess.run([sys.executable, '-m', 'prediction_leaderboard.submit', '-h'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage' in result.stdout
