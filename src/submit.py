import argparse
import os
import sys
from pathlib import Path
import sqlite3
import configparser
import pandas as pd
from datetime import datetime


CONFIG_PATH = 'config.ini'
DB_PATH = 'db/leaderboard.sqlite'


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config['DEFAULT']


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
    from evaluator import metrics as metric_lib

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


def fetch_history(conn, limit, leaderboard_name, tablefmt):
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
    
    # 리더보드명을 예쁘게 출력
    title_length = len(leaderboard_name)
    separator = "=" * (title_length + 4)
    result = f"\n{separator}\n"
    result += f"  {leaderboard_name}\n"
    result += f"{separator}\n\n"
    result += tabulate(table, headers=headers, tablefmt=tablefmt)
    result += f"\n"
    return result


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
    parser.add_argument('--tablefmt', type=str, help='table format (e.g., plain, grid, simple, fancy_grid)')
    parsed = parser.parse_args(args)

    # Convert prediction file path to absolute path before changing working directory
    pred_abs_path = None
    if parsed.pred:
        pred_abs_path = Path(parsed.pred).resolve()
    
    # Change working directory to src directory
    os.chdir(Path(__file__).parent)

    cfg = load_config()
    limit = parsed.n or cfg.get('default_history_limit', 10)
    tablefmt = parsed.tablefmt or cfg.get('tablefmt', 'plain')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    if parsed.pred:
        username = parsed.username or get_git_username()
        public_score, private_score = evaluate(pred_abs_path, cfg)
        insert_submission(conn, username, os.path.basename(parsed.pred), public_score, private_score)

    print(fetch_history(conn, limit, cfg['leaderboard_name'], tablefmt))


if __name__ == '__main__':
    main()
