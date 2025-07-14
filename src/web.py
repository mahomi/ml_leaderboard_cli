import os
import sqlite3
import configparser
from pathlib import Path

import gradio as gr
import pandas as pd

from evaluator import metrics as metric_lib

CONFIG_PATH = 'config.ini'
DB_PATH = 'db/leaderboard.sqlite'

os.chdir(Path(__file__).parent)


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


def evaluate_prediction(pred_path, cfg):
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
        "VALUES (datetime('now'), ?, ?, ?, ?)",
        (username, filename, public_score, private_score),
    )
    conn.commit()


def leaderboard_df(conn, limit, with_private, metric):
    order = 'DESC' if metric == 'f1' else 'ASC'
    cur = conn.execute(
        f'SELECT username, filename, public_score, private_score FROM submissions '
        f'ORDER BY public_score {order} LIMIT ?',
        (limit,),
    )
    rows = cur.fetchall()
    columns = ['Rank', 'Username', 'Filename', 'Public Score']
    if with_private:
        columns.append('Private Score')
    data = []
    for i, row in enumerate(rows, start=1):
        r = [i, row[0], row[1], round(row[2], 4)]
        if with_private:
            r.append(round(row[3], 4))
        data.append(r)
    return pd.DataFrame(data, columns=columns)


def history_df(conn, limit):
    cur = conn.execute(
        'SELECT timestamp, username, filename, public_score FROM submissions ORDER BY id DESC LIMIT ?',
        (limit,),
    )
    rows = cur.fetchall()
    data = [[row[0], row[1], row[2], round(row[3], 4)] for row in rows]
    return pd.DataFrame(data, columns=['Timestamp', 'Username', 'Filename', 'Public Score'])


def submit_action(file, username, history_limit):
    cfg = load_config()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    if file is not None:
        public, private = evaluate_prediction(file.name, cfg)
        insert_submission(conn, username or '-', os.path.basename(file.name), public, private)
    df = history_df(conn, history_limit)
    conn.close()
    return df


def leaderboard_action(limit, with_private):
    cfg = load_config()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    metric = cfg.get('metric', 'rmse')
    df = leaderboard_df(conn, limit, with_private, metric)
    conn.close()
    return df


cfg = load_config()

default_lb_limit = int(cfg.get('default_leaderboard_limit', 10))

default_hist_limit = int(cfg.get('default_history_limit', 10))

with gr.Blocks() as demo:
    with gr.Tab("Leaderboard"):
        lb_n = gr.Number(value=default_lb_limit, precision=0, label="Top N")
        lb_private = gr.Checkbox(label="Show Private Scores")
        lb_refresh = gr.Button("Refresh")
        lb_table = gr.Dataframe(headers=[], interactive=False)
        lb_refresh.click(leaderboard_action, inputs=[lb_n, lb_private], outputs=lb_table)
        demo.load(leaderboard_action, inputs=[lb_n, lb_private], outputs=lb_table)

    with gr.Tab("Submit/History"):
        sub_file = gr.File(label="Prediction CSV")
        sub_user = gr.Text(label="Username")
        hist_n = gr.Number(value=default_hist_limit, precision=0, label="Show N history")
        sub_btn = gr.Button("Submit")
        hist_table = gr.Dataframe(headers=[], interactive=False)
        sub_btn.click(submit_action, inputs=[sub_file, sub_user, hist_n], outputs=hist_table)
        def _load_history(n):
            return submit_action(None, "", n)
        demo.load(_load_history, inputs=[hist_n], outputs=hist_table)

if __name__ == "__main__":
    demo.launch()
