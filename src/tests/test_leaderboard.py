import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 상위 디렉토리를 path에 추가
import sqlite3
import leaderboard
import submit


def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / 'leaderboard.sqlite'
    monkeypatch.setattr(submit, 'DB_PATH', str(db_path))
    monkeypatch.setattr(leaderboard, 'DB_PATH', str(db_path))
    monkeypatch.setattr(submit, 'CONFIG_PATH', os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
    monkeypatch.setattr(leaderboard, 'CONFIG_PATH', os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
    return db_path


def test_leaderboard_output(tmp_path, capsys, monkeypatch):
    db_path = setup_db(tmp_path, monkeypatch)
    submit.main([os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_pred.csv'), 'alice'])
    leaderboard.main([])
    output = capsys.readouterr().out
    assert 'alice' in output
