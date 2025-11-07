"""
stat_analysis.py

Encapsulates statistics analysis. Includes methods for:
    - statistics summaries
    - inferential tests (Welch T Tests and Mann-Whitney Tests)
    - tail tests focused on extreme outliers.
    - Wilcoxon paired tests.
    - Bootstrap CI.
"""
import numpy as np
from scipy import stats


def stat_summary(episodes_df):
    """
    Compute descriptive summaries of episode durations [sec], on raw (count, median, q25, q75, mean) and log10 scale (count, mean, std).
    :param episodes_df: DataFrame containing all episodes.
    :return: dict containing 'summary' and 'summary_log10'.
    """
    ep_df = episodes_df.dropna(subset=["open_type", "duration_sec"]).copy()
    if "duration_log10_sec" not in ep_df.columns:
        ep_df["duration_log10_sec"] = np.log10(ep_df["duration_sec"] + 1)

    summary = ep_df.groupby("open_type")["duration_sec"].agg(
        n="count",
        median="median",
        q25=lambda x: np.percentile(x, 25),
        q75=lambda x: np.percentile(x, 75),
        mean="mean"
    ).reset_index()

    summary_log10 = ep_df.groupby("open_type")["duration_log10_sec"].agg(
        n="count",
        mean="mean",
        sd="std"
    ).reset_index()

    return {
        "summary": summary,
        "summary_log10": summary_log10
    }


def inferential_tests(episodes_df):
    """
    Run episode-level inferential tests comparing duration [sec] distributions between open types.
    :param episodes_df: DataFrame containing all episodes.
    :return: dict containing 'welch_t_test' and 'mann_whitney'.
    """
    ep_df = episodes_df.dropna(subset=["open_type", "duration_sec"]).copy()
    if "duration_log10_sec" not in ep_df.columns:
        ep_df["duration_log10_sec"] = np.log10(ep_df["duration_sec"] + 1)

    auto_log10 = ep_df.loc[ep_df["open_type"] == "auto", "duration_log10_sec"].dropna()
    manual_log10 = ep_df.loc[ep_df["open_type"] == "manual", "duration_log10_sec"].dropna()

    t_res = stats.ttest_ind(auto_log10, manual_log10, equal_var=False)

    auto_raw = ep_df.loc[ep_df["open_type"] == "auto", "duration_sec"].dropna()
    manual_raw = ep_df.loc[ep_df["open_type"] == "manual", "duration_sec"].dropna()
    mw_res = stats.mannwhitneyu(auto_raw,
                                manual_raw,
                                alternative="two-sided")

    return {
        "welch_t_test": t_res,
        "mann_whitney": mw_res
    }


def tail_test(episodes_df):
    """
    Compute diagnostics for the extreme right tail of episode durations [sec].
    :param episodes_df: DataFrame containing all episodes.
    :return: dict containing 'threshold_sec', 'tail_counts', 'total_sum', 'top_sum', 'percent_sum', 'tail_users', 'all_users', 'percent_tail_users' and 'top_user_contrib'.
    """
    ep_df = episodes_df.dropna(subset=["user_id", "open_type", "duration_sec"]).copy()

    threshold = np.percentile(ep_df["duration_sec"], 99)
    tail = ep_df[ep_df["duration_sec"] >= threshold]

    total_sum_by_open_type = ep_df.groupby("open_type")["duration_sec"].sum()
    top_sum_by_open_type = tail.groupby("open_type")["duration_sec"].sum()
    percent_top_sum_out_of_total = (top_sum_by_open_type / total_sum_by_open_type * 100).fillna(0)

    tail_counts = tail["open_type"].value_counts()
    tail_users = tail["user_id"].unique()
    all_users = ep_df["user_id"].unique()
    percent_of_top_users = len(tail_users) / len(all_users) * 100

    top_user_contrib = (
        tail.groupby("open_type")["duration_sec"].agg(
            count="count",
            sum="sum",
        ).sort_values(by="sum", ascending=False).reset_index()
    )

    return {
        "threshold_sec": float(threshold),
        "tail_counts": tail_counts,
        "total_sum": total_sum_by_open_type,
        "top_sum": top_sum_by_open_type,
        "percent_sum": percent_top_sum_out_of_total,
        "tail_users": len(tail_users),
        "all_users": len(all_users),
        "percent_tail_users": percent_of_top_users,
        "top_user_contrib": top_user_contrib
    }


def wilcoxon_paired_test(episodes_df):
    """
    Compute paired Wilcoxon test on per-user median durations [sec].
    :param episodes_df: DataFrame containing all episodes.
    :return: dict containing 'wilcoxon_pair_test', 'n_paired', 'median_auto_sec', 'median_auto_sec', 'median_log10_diff', 'pivot_auto' and 'pivot_manual'.
    """
    ep_df = episodes_df.dropna(subset=["user_id", "open_type", "duration_sec"]).copy()
    per_user = ep_df.groupby(["user_id", "open_type"], as_index=False)["duration_sec"].median()
    pivot = per_user.pivot(index="user_id", columns="open_type", values="duration_sec").dropna()
    auto_log10_median = np.log10(pivot["auto"] + 1)
    manual_log10_median = np.log10(pivot["manual"] + 1)
    wilcoxon_pair_test = stats.wilcoxon(auto_log10_median, manual_log10_median, alternative="two-sided")
    return {
        "wilcoxon_pair_test": wilcoxon_pair_test,
        "n_paired": pivot.shape[0],
        "median_auto_sec": np.median(pivot["auto"]),
        "median_manual_sec": np.median(pivot["manual"]),
        "median_log10_diff": np.median(auto_log10_median - manual_log10_median),
        "pivot_auto": pivot["auto"].values,
        "pivot_manual": pivot["manual"].values
    }


def bootstrap_ci(a, b, n_boot=4000, seed=None):
    """
    Compute bootstrap 95% confidence intervals for two effect estimates computed on paired arrays a and b.
    :param a: raw duration [sec] for condition A.
    :param b: raw duration [sec] for condition B.
    :param n_boot: number of bootstrap resamples. defaults to 4000.
    :param seed: random seed for reproducibility. defaults to None.
    :return: dict containing 'median_ratio_ci' and 'mean_log10_factor_ci'.
    """
    rng = np.random.RandomState(seed)
    a = np.asarray(a)
    b = np.asarray(b)
    a_log10 = np.log10(a + 1)
    b_log10 = np.log10(b + 1)
    if len(a_log10) == 0 or len(b_log10) == 0:
        return None

    obs_median = float(np.median(a) / np.median(b))
    obs_mean_log10 = float(10 ** (np.mean(a_log10) - np.mean(b_log10)))
    boot_median = np.empty(n_boot)
    boot_mean_log10 = np.empty(n_boot)
    for i in range(n_boot):
        a_s_median = rng.choice(a, size=len(a), replace=True)
        b_s_median = rng.choice(b, size=len(b), replace=True)
        boot_median[i] = np.median(a_s_median) / np.median(b_s_median)

        a_s_mean_log10 = rng.choice(a_log10, size=len(a_log10), replace=True)
        b_s_mean_log10 = rng.choice(b_log10, size=len(b_log10), replace=True)
        boot_mean_log10[i] = 10 ** (np.mean(a_s_mean_log10) - np.mean(b_s_mean_log10))
    lower_median, upper_median = np.percentile(boot_median, [2.5, 97.5])
    lower_mean_log10, upper_mean_log10 = np.percentile(boot_mean_log10, [2.5, 97.5])
    return {
        "median_ratio_ci": (obs_median, float(lower_median), float(upper_median)),
        "mean_log10_factor_ci": (obs_mean_log10, float(lower_mean_log10), float(upper_mean_log10))
    }


def all_stat_analysis(episodes_df):
    """
    Runs all statistical analysis functions.
    :param episodes_df: DataFrame containing all episodes.
    :return: dict encapsulating all statistical analysis results.
    """
    results = {}

    summaries = stat_summary(episodes_df)
    results.update(summaries)

    inf_test_results = inferential_tests(episodes_df)
    results["inf"] = inf_test_results

    tail_results = tail_test(episodes_df)
    results["tail"] = tail_results

    wilcoxon_results = wilcoxon_paired_test(episodes_df)
    results["wilcoxon"] = {
        k: v for k, v in wilcoxon_results.items() if k not in ("pivot_auto", "pivot_manual")
    }
    pivot_auto = np.asarray(wilcoxon_results["pivot_auto"])
    pivot_manual = np.asarray(wilcoxon_results["pivot_manual"])

    seed = 42
    boot_ci_results = bootstrap_ci(pivot_auto, pivot_manual, seed=seed)
    results["bootstrap"] = boot_ci_results

    return results
