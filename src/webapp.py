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
    leaderboard_name = cfg.get('leaderboard_name', 'Leaderboard')
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
    return df, leaderboard_name


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
        history_df = get_history_df()
        leaderboard_df, leaderboard_name = get_leaderboard_df()
        return history_df, mask_private_score(leaderboard_df)
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
    history_df = get_history_df()
    leaderboard_df, leaderboard_name = get_leaderboard_df()
    return history_df, mask_private_score(leaderboard_df)


def mask_private_score(df):
    df = df.copy()
    if 'Private Score' in df.columns:
        df = df.drop(columns=['Private Score'])
    return df


def build_app():
    with gr.Blocks() as demo:
        with gr.Tab("Leaderboard") as leaderboard_tab:
            leaderboard_df, leaderboard_name = get_leaderboard_df()
            gr.Markdown(f"# {leaderboard_name}")
            leaderboard_table = gr.Dataframe(value=mask_private_score(leaderboard_df), label="Leaderboard")
            refresh_btn = gr.Button("Refresh")
            def update_leaderboard_table():
                df, name = get_leaderboard_df()
                return mask_private_score(df)
            refresh_btn.click(update_leaderboard_table, outputs=leaderboard_table)
            leaderboard_tab.select(update_leaderboard_table, None, leaderboard_table)
        with gr.Tab("Submit / History"):
            username = gr.Textbox(label="Username")
            file_input = gr.File(label="Prediction CSV")
            submit_btn = gr.Button("Submit")
            history_table = gr.Dataframe(value=get_history_df(), label="History")
            submit_btn.click(handle_submit, inputs=[file_input, username], outputs=[history_table, leaderboard_table])
        with gr.Tab("Leaderboard(Private)") as private_leaderboard_tab:
            private_leaderboard_df, private_leaderboard_name = get_leaderboard_df()
            gr.Markdown(f"# {private_leaderboard_name} (Private)")
            private_leaderboard_table = gr.Dataframe(value=private_leaderboard_df, label="Leaderboard (Private)")
            private_refresh_btn = gr.Button("Refresh")
            def update_private_leaderboard_table():
                df, name = get_leaderboard_df()
                return df
            private_refresh_btn.click(update_private_leaderboard_table, outputs=private_leaderboard_table)
            private_leaderboard_tab.select(update_private_leaderboard_table, None, private_leaderboard_table)
    return demo


if __name__ == '__main__':
    build_app().launch()
