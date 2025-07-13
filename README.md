## ML Leaderboard for CLI

### 1. Overview

* **Project Name:** ML Prediction Leaderboard System for CLI
* **Objective:** Build a CLI-based platform that allows users to submit the prediction results (CSV) of machine learning models trained on a dataset and compare their performance on a leaderboard.

---

### 2. Key Features

#### 2.1 User Interface

* CLI-based submission and result viewing of prediction CSV files (no GUI)

#### 2.2 Data Processing and Evaluation Logic

* Available evaluation metrics (configurable via a settings file; default: `rmse`):

  * `rmse`: Root Mean Squared Error *(default)*
  * `mae`: Mean Absolute Error
  * `mse`: Mean Squared Error
  * `f1`: F1 Score *(only used for binary or multiclass classification tasks)*

* Auto-scoring system: compares submitted prediction CSV with ground truth to compute scores

* **Leaderboard update timing:** Only when a CSV prediction file is passed as an argument to `leaderboard.py`

* Public/Private scores and submission history are stored in a local SQLite database

#### 2.3 Leaderboard System

* Output Modes:

  1. **Leaderboard Mode** (default)

     * Columns: `Rank`, `Username`, `Filename`, `Public Score`, `Private Score`
     * `Private Score` is only shown when `--with-private` option is used

  2. **Submission History Mode** (`--history`)

     * Columns: `Timestamp`, `Username`, `Filename`, `Public Score`

* Username is automatically extracted from Git config

* No login, server, or web environment required

* Output Examples:

  **Leaderboard Mode Output Example:**

  ```
  Rank | Username   | Filename           | Public Score | Private Score
  --------------------------------------------------------------
    1  | alice      | run42.csv          |     0.1234    |     0.1302
    2  | bob        | exp01.csv          |     0.1278    |     0.1351
    3  | charlie    | baseline.csv       |     0.1300    |     0.1409
  ```

  *(If `--with-private` is not used, the `Private Score` column is omitted)*

  **Submission History Mode Output Example:**

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

* Managed via a `config.yaml` file in YAML format
Below are the key fields and their descriptions:
| Field Name             | Description                                                                       | Example Value(s)        | Allowed Values / Notes                                                             |
| ---------------------- | --------------------------------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------- |
| `public_ground_truth`  | Path to the CSV file containing ground truth labels for the **public test** set.  | `./data/public_gt.csv`  | Must be a valid relative or absolute path to a CSV file.                           |
| `private_ground_truth` | Path to the CSV file containing ground truth labels for the **private test** set. | `./data/private_gt.csv` | Must be a valid relative or absolute path to a CSV file.                           |
| `top_k`                | Number of top submissions to show in the leaderboard output.                      | `10`                    | Positive integer (e.g., 1, 5, 10, 20, ...)                                         |
| `metric`               | Evaluation metric to use when scoring predictions.                                | `rmse`                  | `rmse`, `mae`, `mse`, `f1`<br>*`f1` should only be used for classification tasks.* |

* Example Fields:

  * `public_ground_truth`: ./data/public\_gt.csv
  * `private_ground_truth`: ./data/private\_gt.csv
  * `top_k`: 10
  * `metric`: rmse

---

### 5. Execution Commands & Arguments

* `uv run leaderboard.py`: Display leaderboard
* `uv run leaderboard.py --with-private`: Display leaderboard, including private score in output
* `uv run leaderboard.py pred.csv`: Submit and evaluate. Display submission history
* `uv run leaderboard.py --history`: Display submission history

---

### 6. File Structure and Test Setup

```
prediction_leaderboard/
├── leaderboard.py              # CLI script for evaluation and leaderboard display
├── config.yaml                 # Configuration file (GT paths, display options, etc.)
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
    ├── test_leaderboard.py     # Tests for submission and leaderboard update
    └── test_cli_commands.py    # Tests for CLI command behavior
```
