import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import sqlite3
import yaml
import pandas as pd
from datetime import datetime
from prediction_leaderboard.evaluator import metrics as metric_lib

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'leaderboard.sqlite')


def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def init_db(conn):
    conn.execute(
        'CREATE TABLE IF NOT EXISTS submissions('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'timestamp TEXT,'
        'username TEXT,'
        'filename TEXT,'
        'public_score REAL,'
        'private_score REAL)'
    )
    conn.commit()


def evaluate(pred_path, cfg):
    metric_name = cfg.get('metric', 'rmse')
    metric_func = metric_lib.METRICS[metric_name]
    public_gt = pd.read_csv(cfg['public_ground_truth'])['label']
    private_gt = pd.read_csv(cfg['private_ground_truth'])['label']
    pred = pd.read_csv(pred_path)['prediction']
    public_score = metric_func(public_gt, pred)
    private_score = metric_func(private_gt, pred)
    return public_score, private_score


def insert_submission(conn, username, filename, public_score, private_score):
    conn.execute(
        'INSERT INTO submissions(timestamp, username, filename, public_score, private_score) '
        'VALUES (?, ?, ?, ?, ?)',
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), username, filename, public_score, private_score)
    )
    conn.commit()


def fetch_history(conn, limit):
    cur = conn.execute(
        'SELECT timestamp, username, filename, public_score FROM submissions ORDER BY id DESC LIMIT ?',
        (limit,)
    )
    rows = cur.fetchall()
    headers = ["Timestamp", "Username", "Filename", "Public Score"]
    table = []
    for row in rows:
        table.append([row[0], row[1], row[2], f"{row[3]:.4f}"])
    from tabulate import tabulate
    return tabulate(table, headers=headers, tablefmt="plain")


def get_git_username():
    try:
        import subprocess
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        name = result.stdout.strip()
        return name or '-'
    except Exception:
        return '-'


def main(args=None):
    parser = argparse.ArgumentParser(description='Submit prediction file or show history')
    parser.add_argument('pred', nargs='?', help='prediction CSV file')
    parser.add_argument('username', nargs='?', help='username for submission')
    parser.add_argument('-n', type=int, help='number of history entries to show')
    parsed = parser.parse_args(args)

    cfg = load_config()
    limit = parsed.n or cfg.get('default_history_limit', 10)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    if parsed.pred:
        username = parsed.username or get_git_username()
        public_score, private_score = evaluate(parsed.pred, cfg)
        insert_submission(conn, username, os.path.basename(parsed.pred), public_score, private_score)

    print(fetch_history(conn, limit))


if __name__ == '__main__':
    main()
