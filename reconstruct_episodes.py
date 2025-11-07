"""
reconstruct_episodes.py

Encapsulates reconstruction logic. Uses EpisodeType Enum to mark episodes as either:
    - REGULAR
    - DOUBLE_OPEN
    - ORPHAN_OPEN
    - ORPHAN_CLOSE
"""
from enum import Enum
import pandas as pd
import numpy as np


class EpisodeType(str, Enum):
    REGULAR = "regular"
    DOUBLE_OPEN = "double_open"
    ORPHAN_OPEN = "orphan_open"
    ORPHAN_CLOSE = "orphan_close"


def append_episode(episodes, user_id, open_event, close_event, episode_type):
    """
    Helper function to add an episode entry to the episodes list.
    :param episodes: List of episodes, containing 'user_id', 'open_timestamp', 'close_timestamp', 'open_type' and 'episode_type'.
    :param user_id: id of user whose episode entry is to be added.
    :param open_event: event that starts the episode being added.
    :param close_event: event that ends the episode being added.
    :param episode_type: EpisodeType.
    :return: None
    """
    episodes.append({
        "user_id": user_id,
        "open_timestamp": open_event["timestamp"] if open_event is not None else None,
        "close_timestamp": close_event["timestamp"] if close_event is not None else None,
        "open_type": open_event["open_type"] if open_event is not None else None,
        "episode_type": episode_type,
    })


def reconstruct_user_episodes(user_id, user_events):
    """
    Reconstruct episodes for a single user.
    :param user_id: id of user whose episodes are to be reconstructed.
    :param user_events: events being reconstructed.
    :return: List of episode entries.
    """
    episodes = []
    last_open_event = None

    for _, row in user_events.iterrows():
        # print(f"\t{row['event']} {row['datetime']} {row['open_type']}")
        if row["event"] == "opened":
            if last_open_event is not None:
                # double opened event
                append_episode(episodes, user_id, last_open_event, row, EpisodeType.DOUBLE_OPEN)
            last_open_event = row
        elif row["event"] == "closed":
            if last_open_event is not None:
                # regular open-close episode
                append_episode(episodes, user_id, last_open_event, row, EpisodeType.REGULAR)
                last_open_event = None
            else:
                # orphan closed event
                append_episode(episodes, user_id, None, row, EpisodeType.ORPHAN_CLOSE)

    if last_open_event is not None:
        # Opened event at the end
        append_episode(episodes, user_id, last_open_event, None, EpisodeType.ORPHAN_OPEN)

    return episodes


def reconstruct_all_episodes(dataset_df):
    """
    Reconstruct all episodes from dataset.
    :param dataset_df: Dataframe containing all data from the dataset.
    :return: DataFrame containing all episode entries.
    """
    all_episodes = []
    dataset_df = dataset_df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
    for user_id, group in dataset_df.groupby("user_id"):
        # print(f"\nUser {user_id}:")
        user_episodes = reconstruct_user_episodes(user_id, group)
        all_episodes.extend(user_episodes)
    return pd.DataFrame(all_episodes)


def read_and_reconstruct_episodes(df):
    """
    Read and reconstruct all episodes from a DataFrame.
    :param df: DataFrame containing all data from the dataset.
    :return: DataFrame containing all regular episodes.
    """
    # Add 'datetime' column to dataset
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")

    episodes_df = reconstruct_all_episodes(df)

    episodes_df["duration_ms"] = episodes_df["close_timestamp"] - episodes_df["open_timestamp"]
    episodes_df["duration_sec"] = episodes_df["duration_ms"] / 1000
    episodes_df["duration_log10_sec"] = np.log10(episodes_df["duration_sec"] + 1)
    return episodes_df
