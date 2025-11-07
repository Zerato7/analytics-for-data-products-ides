"""
plotting.py

Encapsulates logic for generating plots. Data is visualized through:
    - Histogram (log10)
    - Boxplot (log10)
    - Boxplot of per user medians (log10)
    - Violin
"""
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_hist_log10(episodes_df, out_dir, out_file_name="duration_hist_log10.png", bins=50):
    """
    Histogram of log10(duration_sec + 1) for manual vs auto.
    :param episodes_df: DataFrame containing episodes. Must contain: open_type, duration_sec.
    :param out_dir: directory where to save plot image.
    :param out_file_name: file name (default 'duration_hist_log10.png') for saving plot image.
    :param bins: bins (default 50) for histogram.
    :return: None
    """
    ep_df = episodes_df.dropna(subset=["open_type", "duration_sec"])
    if ep_df.empty:
        raise ValueError("No episodes with 'open_type'/'duration_sec' found.")
    plt.figure(figsize=(8, 5))

    for o_type in ep_df["open_type"].unique():
        subset = ep_df[ep_df["open_type"] == o_type]
        sns.histplot(subset["duration_log10_sec"], bins=bins, stat="density",
                     element="step", label=o_type, alpha=0.6)
    plt.xlabel("log10(duration_sec + 1)")
    plt.title("Histogram (log10) by open_type")
    plt.legend(title="open_type")
    plt.tight_layout()
    out_path = Path(out_dir) / out_file_name
    plt.savefig(str(out_path))
    plt.close()


def plot_boxplot_log10(episodes_df, out_dir, out_file_name="duration_boxplot_log10.png"):
    """
    Boxplot of log10(duration_sec + 1) for manual vs auto.
    :param episodes_df: DataFrame containing episodes. Must contain: open_type, duration_sec.
    :param out_dir: directory where to save plot image.
    :param out_file_name: file name (default 'duration_boxplot_log10.png') for saving plot image.
    :return: None
    """
    ep_df = episodes_df.dropna(subset=["open_type", "duration_sec"])
    if ep_df.empty:
        raise ValueError("No episodes with 'open_type'/'duration_sec' found.")

    plt.figure(figsize=(6, 5))
    sns.boxplot(x="open_type", y="duration_log10_sec", data=ep_df)
    plt.xlabel("open_type")
    plt.ylabel("log10(duration_sec + 1)")
    plt.title("Boxplot duration (log10) by open_type")
    plt.tight_layout()
    out_path = Path(out_dir) / out_file_name
    plt.savefig(str(out_path))
    plt.close()


def plot_per_user_median_boxplot(episodes_df, out_dir, out_file_name="boxplot_per_user_median_log10.png"):
    """
    Boxplot of per-user median log10 duration grouped by open_type.
    :param episodes_df: DataFrame containing episodes. Must contain: user_id, open_type, duration_sec.
    :param out_dir: directory where to save plot image.
    :param out_file_name: file name (default 'boxplot_per_user_median_log10.png') for saving plot image.
    :return: None
    """
    ep_df = episodes_df.dropna(subset=["user_id", "open_type", "duration_sec"])
    if ep_df.empty:
        raise ValueError("No episodes with 'user_id'/'open_type'/'duration_sec' found.")

    per_user = ep_df.groupby(["user_id", "open_type"], as_index=False)["duration_sec"].median()
    per_user["log10_median"] = np.log10(per_user["duration_sec"] + 1)

    plt.figure(figsize=(6, 5))
    sns.boxplot(x="open_type", y="log10_median", data=per_user)
    plt.xlabel("open_type")
    plt.ylabel("log10(per-user median duration_sec + 1)")
    plt.title("Per-user median duration (log10) by open_type")
    plt.tight_layout()
    out_path = Path(out_dir) / out_file_name
    plt.savefig(str(out_path))
    plt.close()


def plot_violin_log10(episodes_df, out_dir, out_file_name="duration_violin_log10.png", cut=2):
    """
    Violin plot of log10(duration_sec + 1) by open_type.
    :param episodes_df: DataFrame containing episodes. Must contain: open_type, duration_sec.
    :param out_dir: directory where to save plot image.
    :param out_file_name: file name (default 'violin_log10.png') for saving plot image.
    :param cut: cut for violin plot.
    :return: None
    """
    ep_df = episodes_df.dropna(subset=["user_id", "open_type", "duration_sec"])
    if ep_df.empty:
        raise ValueError("No episodes with 'user_id'/'open_type'/'duration_sec' found.")

    plt.figure(figsize=(6, 5))
    sns.violinplot(x="open_type", y="duration_log10_sec", data=ep_df, cut=cut)
    plt.xlabel("open_type")
    plt.ylabel("log10(duration_sec + 1)")
    plt.title("Violin plot (log10) by open_type")
    plt.tight_layout()
    out_path = Path(out_dir) / out_file_name
    plt.savefig(str(out_path))
    plt.close()


def plot_all(episodes_df, out_dir):
    """
    Runs plot_hist_log10, plot_boxplot_log10, plot_per_user_median_log10, plot_violin_log10.
    :param episodes_df: DataFrame containing episodes. Must contain: user_id, open_type, duration_sec.
    :param out_dir: directory where to save plot images.
    :return: None
    """
    plot_hist_log10(episodes_df, out_dir)
    plot_boxplot_log10(episodes_df, out_dir)
    plot_per_user_median_boxplot(episodes_df, out_dir)
    plot_violin_log10(episodes_df, out_dir)
