"""
main.py

Modes for --mode:
    - regular_only          : use only episodes where episode_type == 'regular'
    - include_double_open   : include episode_type == 'double_open' by folding them into regular episodes

Trim options for --trim:
    - all                   : use all selected episodes
    - exclude_top1          : remove episodes whose duration_sec >= 99th percentile (computed within selected episodes)

Default:
    - mode: regular_only
    - trim: all
    - csv: toolwindow_data.csv
    - plots: False

Usage examples:
    - python main.py --mode regular_only --trim all --plots True
    - python main.py --mode include_double_open --trim exclude_top1 --csv toolwindow.csv
"""
import argparse
from pathlib import Path

import pandas as pd
import numpy as np

from io_driver import pretty_print, save_json
from plotting import plot_all
from reconstruct_episodes import read_and_reconstruct_episodes, EpisodeType
from stat_analysis import all_stat_analysis


def load_csv(path):
    """
    Reads data from csv file.
    :param path: file path to csv file.
    :return: DataFrame containing data from csv file.
    """
    return pd.read_csv(path)


def select_mode(df, mode):
    """
    Selects episodes to be included in calculations.
    :param df: DataFrame containing episodes data.
    :param mode: mode determining which episodes to include in calculations.
    :return: DataFrame containing selected episodes.
    """
    if mode == "regular_only":
        return df[df["episode_type"] == EpisodeType.REGULAR].copy()
    if mode == "include_double_open":
        return df[df["episode_type"].isin((EpisodeType.DOUBLE_OPEN, EpisodeType.REGULAR))].copy()
    raise ValueError("Unknown mode:", mode)


def apply_trim(df, trim):
    """
    Trims data based on trim option.
    :param df: DataFrame containing episodes data.
    :param trim: trimming option.
    :return: trimmed DataFrame.
    """
    if trim == "all":
        return df
    if trim == "exclude_top1":
        threshold = np.percentile(df["duration_sec"].dropna(), 99)
        return df[df["duration_sec"] < threshold].copy()
    raise ValueError("Unknown trim:", trim)


def parse_cmd_args():
    """
    Parse command line arguments ('--mode', '--trim', '--csv', '--plots').
    :return: argparse.Namespace object.
    """
    parser = argparse.ArgumentParser(description="Run toolwindow analysis on selected episodes.")
    parser.add_argument("--mode", type=str, default="regular_only",
                        choices=["regular_only", "include_double_open"],)
    parser.add_argument("--trim", type=str, default="all",
                        choices=["all", "exclude_top1"],)
    parser.add_argument("--csv", type=str, default="toolwindow_data.csv",
                        help="path to dataset csv file")
    parser.add_argument("--plots", type=bool, default=False,
                        help="generate plots or not")
    return parser.parse_args()


def create_out_dir(args):
    out_dir = Path("results")/f"{args.mode}_{args.trim}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def main():
    """
    Main function that gets called from main.py, central starting point for entire code.
    :return: None
    """
    args = parse_cmd_args()
    df = load_csv(args.csv)
    episodes_df = read_and_reconstruct_episodes(df)
    selected_df = select_mode(episodes_df, args.mode)
    selected_trimmed_df = apply_trim(selected_df, args.trim)
    out_dir = create_out_dir(args)
    if args.plots:
        plot_all(selected_trimmed_df, out_dir)
    results = all_stat_analysis(selected_trimmed_df)
    pretty_print(results, out_dir)
    save_json(results, out_dir)


if __name__ == "__main__":
    main()
