import os
from pathlib import Path
import sqlite3
import configparser
import pandas as pd
import gradio as gr

# ensure relative paths work like the CLI scripts
os.chdir(Path(__file__).parent)

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


def get_leaderboard_df():
    cfg = load_config()
    metric = cfg.get('metric', 'rmse')
    limit = int(cfg.get('default_leaderboard_limit', 10))
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    order = 'DESC' if metric == 'f1' else 'ASC'
    cur = conn.execute(
        f'SELECT username, filename, public_score, private_score FROM submissions '
        f'ORDER BY public_score {order} LIMIT ?',
        (limit,)
    )
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=['Username', 'Filename', 'Public Score', 'Private Score'])
    df.index += 1
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Rank'}, inplace=True)
    return df


def get_history_df():
    cfg = load_config()
    limit = int(cfg.get('default_history_limit', 10))
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cur = conn.execute(
        'SELECT timestamp, username, filename, public_score FROM submissions ORDER BY id DESC LIMIT ?',
        (limit,)
    )
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=['Timestamp', 'Username', 'Filename', 'Public Score'])
    return df


def handle_submit(file, username):
    import submit
    if file is None:
        return get_history_df(), get_leaderboard_df()
    cfg = load_config()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    public_score, private_score = submit.evaluate(file.name, cfg)
    submit.insert_submission(
        conn,
        username or submit.get_git_username(),
        os.path.basename(file.name),
        public_score,
        private_score,
    )
    return get_history_df(), get_leaderboard_df()


def build_app():
    with gr.Blocks() as demo:
        leaderboard_table = gr.Dataframe(value=get_leaderboard_df(), label="Leaderboard")
        with gr.Tab("Leaderboard"):
            refresh_btn = gr.Button("Refresh")
            refresh_btn.click(lambda: get_leaderboard_df(), outputs=leaderboard_table)
            leaderboard_table.render()
        with gr.Tab("Submit / History"):
            username = gr.Textbox(label="Username")
            file_input = gr.File(label="Prediction CSV")
            submit_btn = gr.Button("Submit")
            history_table = gr.Dataframe(value=get_history_df(), label="History")
            submit_btn.click(handle_submit, inputs=[file_input, username], outputs=[history_table, leaderboard_table])
    return demo


if __name__ == '__main__':
    build_app().launch()
