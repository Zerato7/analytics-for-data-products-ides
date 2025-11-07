# Toolwindow Duration Analysis

Short, runnable analysis comparing "auto" vs "manual" opens.  
Scripts live in repository root. Outputs (JSON, PNG, textual summary) are written to a run-specific folder under `results/`. A LaTeX report is in `report/`.

## Repo layout
- Root scripts: `main.py`, `reconstruct_episodes.py`, `stat_analysis.py`, `plotting.py` and `io_driver.py`
- `results/` - generated output folders (created by `main.py`)
- `report/` - LaTeX source and generated `analysis.pdf`
- `toolwindow_data.csv` - dataset csv file (`main.py` expect this file in root directory)
- `requirements.txt` - Python dependencies

## Requirements
Tested on Python 3.12. Install required packages:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## How to run

`main.py` is the script that need to be run. It uses command-line arguments.

### Args
- `--mode`:
    - `regular_only `         : use only episodes where `episode_type == 'regular'`
    - `include_double_open`   : include `episode_type == 'double_open'` by folding them into regular episodes

- `--trim`:
    - `all`                   : use all selected episodes
    - `exclude_top1`          : remove episodes whose `duration_sec >= 99th percentile` (computed within selected episodes)

- `--csv`: dataset filepath
- `--plots`: `True` or `False`. If `True` generate plot images.

### Default
- `mode`: `regular_only`
- `trim`: `all`
- `csv`: `toolwindow_data.csv`
- `plots`: `False`

### Examples
```bash
python main.py --mode regular_only --trim all --plots True
python main.py --mode include_double_open --trim exclude_top1 --csv toolwindow.csv
```

### Output
Running `main.py` will create a run-specific folder under `results/` named like:
```bash
results/<mode>_<trim>
```
Files written inside that folder
- `analysis.json`
- PNG plots
  - `duration_hist_log10.png`
  - `boxplot_per_user_median_log10.png`
  - `duration_boxplot_log10.png`
  - `duration_violin_log10.png`
- `results.txt`