## ML Leaderboard for CLI

### 1. Overview

* **Project Name:** ML Prediction Leaderboard System for CLI
* **Objective:** Build a CLI-based platform that allows users to submit the prediction results (CSV) of machine learning models trained on a dataset and compare their performance on a leaderboard.

---

### 2. Key Features

#### 2.1 User Interface

* CLI-based submission and result viewing of prediction CSV files (no GUI)
* No login, server, or web environment required

#### 2.2 Data Processing and Evaluation Logic

* Available evaluation metrics (configurable via a settings file; default: `rmse`):

  * `rmse`: Root Mean Squared Error *(default)*
  * `mae`: Mean Absolute Error
  * `mse`: Mean Squared Error
  * `f1`: F1 Score *(only used for binary or multiclass classification tasks)*

* Auto-scoring system: compares submitted prediction CSV with ground truth to compute scores

* **Leaderboard update timing:** Only when a CSV prediction file is passed as an argument to `submit.py`

* Public/Private scores and submission history are stored in a local SQLite database

#### 2.3 Leaderboard System

* **Leaderboard Display** (`leaderboard.py`):

  * Columns: `Rank`, `Username`, `Filename`, `Public Score`, `Private Score`
  * `Private Score` is only shown when `--with-private` option is used

* **Submission History** (`submit.py`):

  * Columns: `Timestamp`, `Username`, `Filename`, `Public Score`

* Output Examples:

  **Leaderboard Display Output Example:**

  ```
  Rank | Username   | Filename           | Public Score | Private Score
  --------------------------------------------------------------
    1  | alice      | run42.csv          |     0.1234    |     0.1302
    2  | bob        | exp01.csv          |     0.1278    |     0.1351
    3  | charlie    | baseline.csv       |     0.1300    |     0.1409
  ```

  *(If `--with-private` is not used, the `Private Score` column is omitted)*

  **Submission History Output Example:**

  ```
  Timestamp           | Username | Filename        | Public Score
  ------------------------------------------------------------
  2025-07-13 14:02:01 | alice    | run42.csv       |     0.1234
  2025-07-13 13:50:22 | alice    | run41.csv       |     0.1241
  2025-07-13 13:15:10 | bob      | exp01.csv       |     0.1278
  ```

---

### 3. Tech Stack

* **Package Management & Execution:** Use [uv](https://github.com/astral-sh/uv)

  * Run: `uv run leaderboard.py`
  * Add package: `uv add <package-name>`

* **Frontend:** None (CLI only)

* **Backend:** None (local execution)

* **Storage:** Local file system

* **Database:** SQLite (for submission history)

* **Evaluation:** Python + numpy/pandas/sklearn

---

### 4. Leaderboard Configuration File

* Managed via a `config.ini` file in INI format
Below are the key fields and their descriptions:

| Field Name                    | Description                                                                       | Example Value           | Allowed Values / Notes                                               |
| ----------------------------- | --------------------------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------- |
| `public_ground_truth`        | Path to the CSV file containing ground truth labels for the **public test** set.  | `./data/public_gt.csv`  | Must be a valid relative or absolute path.                           |
| `private_ground_truth`       | Path to the CSV file containing ground truth labels for the **private test** set. | `./data/private_gt.csv` | Must be a valid relative or absolute path.                           |
| `default_leaderboard_limit`  | Default number of top-ranked submissions to display in **leaderboard display**.      | `10`                    | Positive integer (e.g., 5, 10, 20, ...). Can be overridden with `-n` argument. |
| `default_history_limit`      | Default number of recent submission entries to display in **submission history**. | `10`                    | Positive integer (e.g., 5, 10, 50, ...). Can be overridden with `-n` argument. |
| `metric`                     | Evaluation metric used for scoring predictions.                                   | `rmse`                  | `rmse`, `mae`, `mse`, `f1` (Use `f1` only for classification tasks.) |ls

* Example Fields:
```ini
[DEFAULT]
public_ground_truth = ./data/public_gt.csv
private_ground_truth = ./data/private_gt.csv
default_leaderboard_limit = 10
default_history_limit = 10
metric = rmse
```

---

### 5. Execution Commands & Arguments

#### 5.1 Leaderboard Display Commands (`leaderboard.py`)

* `uv run leaderboard.py [options]`: Display leaderboard

**Options:**
- `-n N`: Number of top submissions to display (default: from config.ini)
- `--with-private`: Include private score in output

#### 5.2 Submission and History Commands (`submit.py`)

* `uv run submit.py [pred.csv] [username] [options]`: Submit prediction file or display submission history

**Arguments:**
- `pred.csv`: Path to the prediction CSV file
  - **If provided**: Submit and evaluate the prediction file, then display submission history
  - **If omitted**: Display submission history only
- `[username]`: Username for the submission (only used when `pred.csv` is provided)
  - **If provided**: Use the specified username for submission
  - **If omitted**: Automatically extract username from Git config (`git config user.name`)
  - **If Git config is not available**: Uses '-' as the username

**Options:**
- `-n N`: Number of recent submissions to display (default: from config.ini)

**Note:** The functionality has been separated into two distinct files to provide clearer separation of concerns:
- `leaderboard.py`: Focuses on displaying leaderboard rankings
- `submit.py`: Handles prediction file submission and submission history viewing

**Usage Examples:**

*Leaderboard Display:*
```bash
# Display top 10 submissions (default)
uv run leaderboard.py

# Display top 5 submissions with private scores
uv run leaderboard.py -n 5 --with-private

# Display top 20 submissions without private scores
uv run leaderboard.py -n 20
```

*Submission and History:*
```bash
# Display recent submission history (default 10 entries)
uv run submit.py

# Display recent 20 submission entries
uv run submit.py -n 20

# Submit prediction file with auto-detected username
uv run submit.py my_prediction.csv

# Submit prediction file with custom username
uv run submit.py my_prediction.csv alice

# Submit prediction file and show top 5 recent submissions
uv run submit.py my_prediction.csv -n 5
```

---

### 6. File Structure and Test Setup

```
src/
├── leaderboard.py              # CLI script for leaderboard display only
├── submit.py                   # CLI script for submission and history management
├── config.ini                  # Configuration file (GT paths, display options, etc.)
├── data/
│   ├── public_gt.csv           # Example Public Test ground truth
│   ├── private_gt.csv          # Example Private Test ground truth
│   └── sample_pred.csv         # Sample prediction submission file
├── db/
│   └── leaderboard.sqlite      # SQLite DB file
├── evaluator/
│   └── metrics.py              # Evaluation metric implementations
└── tests/                      # pytest-based test cases
    ├── test_metrics.py         # Tests for evaluation metrics
    ├── test_leaderboard.py     # Tests for leaderboard display
    ├── test_submit.py          # Tests for submission functionality
    └── test_cli_commands.py    # Tests for CLI command behavior
```
