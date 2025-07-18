import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 상위 디렉토리를 path에 추가
import sqlite3
import submit


def test_submission(tmp_path, monkeypatch):
    db_path = tmp_path / 'leaderboard.sqlite'
    monkeypatch.setattr(submit, 'DB_PATH', str(db_path))
    monkeypatch.setattr(submit, 'CONFIG_PATH', os.path.join(os.path.dirname(__file__), '..', 'config.ini'))

    submit.main([os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_pred.csv'), 'alice'])

    conn = sqlite3.connect(db_path)
    cur = conn.execute('SELECT COUNT(*) FROM submissions')
    count = cur.fetchone()[0]
    assert count == 1
