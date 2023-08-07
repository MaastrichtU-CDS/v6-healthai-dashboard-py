# -*- coding: utf-8 -*-

""" Get survival rate profiles
"""
import pandas as pd


def survival_rate(df: pd.DataFrame, cutoff: int, delta: int) -> list:
    """ Compute survival rate at certain time points after diagnosis

    Parameters
    ----------
    df
        DataFrame with TNM data
    cutoff
        Maximum number of days for the survival rate profile
    delta
        Number of days between the time points in the profile

    Returns
    -------
    survival_rates
        Survival rate profile
    """

    # Get survival days, here we assume the date of last follow-up as death date
    df['date_of_diagnosis'] = pd.to_datetime(df['date_of_diagnosis'])
    df['date_of_fu'] = pd.to_datetime(df['date_of_fu'])
    df['survival_days'] = df.apply(
        lambda x: (x['date_of_fu'] - x['date_of_diagnosis']).days, axis=1
    )

    # Get survival rate after a certain number of days
    times = list(range(0, cutoff, delta))
    all_alive = len(df[df['vital_status'] == 'alive'])
    all_dead = len(df[df['vital_status'] == 'dead'])
    survival_rates = []
    for time in times:
        dead = len(df[df['survival_days'] <= time])
        alive = (all_dead - dead) + all_alive
        survival_rates.append(alive / len(df))

    return survival_rates
