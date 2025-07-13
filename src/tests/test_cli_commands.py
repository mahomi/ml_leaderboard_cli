import subprocess
import sys
import os


def test_leaderboard_help():
    original_cwd = os.getcwd()
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run([sys.executable, '../leaderboard.py', '-h'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage' in result.stdout
    finally:
        os.chdir(original_cwd)


def test_submit_help():
    original_cwd = os.getcwd()
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run([sys.executable, '../submit.py', '-h'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage' in result.stdout
    finally:
        os.chdir(original_cwd)
