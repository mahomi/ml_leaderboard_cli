import os
import sqlite3
from prediction_leaderboard import submit


def test_submission(tmp_path, monkeypatch):
    db_path = tmp_path / 'leaderboard.sqlite'
    monkeypatch.setattr(submit, 'DB_PATH', str(db_path))
    monkeypatch.setattr(submit, 'CONFIG_PATH', os.path.join(os.path.dirname(__file__), '..', 'config.yaml'))

    submit.main([os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_pred.csv'), 'alice'])

    conn = sqlite3.connect(db_path)
    cur = conn.execute('SELECT COUNT(*) FROM submissions')
    count = cur.fetchone()[0]
    assert count == 1
