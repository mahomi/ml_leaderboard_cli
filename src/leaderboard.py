import argparse
import os
import sys
from pathlib import Path
import sqlite3
import configparser
from tabulate import tabulate

os.chdir(Path(__file__).parent)

from evaluator import metrics

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


def fetch_leaderboard(conn, limit, with_private, metric, leaderboard_name, tablefmt):
    order = 'DESC' if metric == 'f1' else 'ASC'
    cur = conn.execute(
        f'SELECT username, filename, public_score, private_score FROM submissions '
        f'ORDER BY public_score {order} LIMIT ?',
        (limit,)
    )
    rows = cur.fetchall()
    headers = ["Rank", "Username", "Filename", "Public Score"]
    if with_private:
        headers.append("Private Score")
    table = []
    for i, row in enumerate(rows, start=1):
        r = [i, row[0], row[1], f"{row[2]:.4f}"]
        if with_private:
            r.append(f"{row[3]:.4f}")
        table.append(r)
    
    # 리더보드명을 예쁘게 출력
    title_length = len(leaderboard_name)
    separator = "=" * (title_length + 4)
    result = f"\n{separator}\n"
    result += f"  {leaderboard_name}\n"
    result += f"{separator}\n\n"
    result += tabulate(table, headers=headers, tablefmt=tablefmt)
    # result += f"\n\n{separator}\n"
    result += f"\n"
    return result


def main(args=None):
    parser = argparse.ArgumentParser(description="Display leaderboard")
    parser.add_argument('-n', type=int, help='number of top submissions to display')
    parser.add_argument('--with-private', action='store_true', help='show private scores')
    parser.add_argument('--tablefmt', type=str, help='table format (e.g., plain, grid, simple, fancy_grid)')
    parsed = parser.parse_args(args)

    cfg = load_config()
    limit = parsed.n or cfg.get('default_leaderboard_limit', 10)
    tablefmt = parsed.tablefmt or cfg.get('tablefmt', 'plain')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    metric = cfg.get('metric', 'rmse')
    leaderboard_name = cfg.get('leaderboard_name', 'Leaderboard')
    print(fetch_leaderboard(conn, limit, parsed.with_private, metric, leaderboard_name, tablefmt))


if __name__ == '__main__':
    main()
