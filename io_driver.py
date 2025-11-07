"""
io_driver.py

Encapsulates io logic. Both printing stat_analysis data to console and saving it to json file.
"""
import io
from contextlib import redirect_stdout
from pathlib import Path

from tabulate import tabulate
import json

import pandas as pd


def _print_df(df, floatfmt=".3f"):
    """
    Prints DataFrame to console.
    :param df: DataFrame to be printed.
    :param floatfmt: float point format.
    :return: None
    """
    print(tabulate(df, headers="keys", floatfmt=floatfmt, showindex=False, tablefmt="github"))


def pretty_print(results, out_dir, filename="results.txt"):
    """
    Prints results of stat_analysis to standard output and saves it to file.
    :param results: object containing data to be printed.
    :param out_dir: directory where results will be saved.
    :param filename: name of the file to be saved.
    :return: None
    """
    buf = io.StringIO()

    with redirect_stdout(buf):
        print("\n--- Summary statistics (raw seconds) ---")
        _print_df(results["summary"])
        print("\n--- Summary statistics (log10 scale) ---")
        _print_df(results["summary_log10"])

        print("\n--- Inferential tests ---")
        print("Welch t-test on log10(duration_sec+1):")
        print(results["inf"]["welch_t_test"])
        print("Mann-Whitney on raw seconds:")
        print(results["inf"]["mann_whitney"])

        print("\n--- Top 1% tail diagnostics ---")
        print(f"Threshold [sec]: {results['tail']['threshold_sec']:.3f}")
        print("Top counts by open_type:")
        print(results["tail"]["tail_counts"].to_string())
        print("\nTotal seconds by open_type:")
        print(results["tail"]["total_sum"].to_string())
        print("\nTop seconds by open_type:")
        print(results["tail"]["top_sum"].to_string())
        print("\nTop percent by open_type:")
        print(results["tail"]["percent_sum"].to_string())
        print(f"Number of users with top 1% episodes: {results['tail']['tail_users']}")
        print(f"Total number of users: {results['tail']['all_users']}")
        print(f"Percent wise: {results['tail']['percent_tail_users']:.2f}%")

        if not results["tail"]["top_user_contrib"].empty:
            print("\nTop user contributors:")
            _print_df(results["tail"]["top_user_contrib"])

        print("\n--- Wilcoxon Paired Test ---")
        print(f"n_paired: {results['wilcoxon']['n_paired']}")
        print(results["wilcoxon"]["wilcoxon_pair_test"])
        print(f"Median auto [sec]: {results['wilcoxon']['median_auto_sec']}")
        print(f"Median manual [sec]: {results['wilcoxon']['median_manual_sec']}")
        print(f"Median log10 diff: {results['wilcoxon']['median_log10_diff']}")

        print("\n--- Bootstrap CI ---")
        print(results["bootstrap"]["median_ratio_ci"])
        print(results["bootstrap"]["mean_log10_factor_ci"])

    text = buf.getvalue()
    print(text, end="")

    out_path = Path(out_dir) / filename
    out_path.write_text(text, encoding="utf-8")


def _make_json(obj):
    """
    Converts a Python object to a JSON object.
    :param obj: object to convert.
    :return: JSON object.
    """
    if isinstance(obj, dict):
        return {k: _make_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json(v) for v in obj]
    if isinstance(obj, (str, int, bool, float)) or obj is None:
        return obj
    if isinstance(obj, pd.Series):
        return _make_json(obj.to_dict())
    if isinstance(obj, pd.DataFrame):
        return _make_json(obj.to_dict(orient="records"))
    return str(obj)


def save_json(results, out_dir, filename="analysis.json"):
    """
    Converts and saves results to a JSON file.
    :param results: obj to convert and save as json.
    :param out_dir: directory where to save json file.
    :param filename: file path to save json.
    :return: None
    """
    json_obj = _make_json(results)
    path = Path(out_dir) / filename
    with path.open("w", encoding="utf8") as f:
        json.dump(json_obj, f, indent=2)
