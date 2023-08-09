# -*- coding: utf-8 -*-

""" Federated algorithm

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is sent to the central server.
"""
import time
import pandas as pd

from vantage6.tools.util import info
from v6_healthai_dashboard_py.survival import survival_rate


def master(
        client, data: pd.DataFrame, org_ids: list = None,
        cutoff: int = 730, delta: int = 30
) -> dict:
    """ Master algorithm

    Parameters
    ----------
    client
        Vantage6 user or mock client
    data
        DataFrame with the TNM data
    org_ids
        List with organisation ids to be used
    cutoff
        Maximum number of days for the survival rate profile
    delta
        Number of days between the time points in the profile

    Returns
    -------
    results
        Dictionary with the final orchestrated result
    """

    # Get all organization ids that are within the collaboration,
    # if they were not provided
    # FlaskIO knows the collaboration to which the container belongs
    # as this is encoded in the JWT (Bearer token)
    info('Collecting participating organizations')
    organizations = client.get_organizations_in_my_collaboration()
    ids = [organization.get('id') for organization in organizations
           if not org_ids or organization.get('id') in org_ids]

    # The input for the algorithm, which is the same for all organizations
    info('Defining input parameters')
    input_ = {
        'method': 'statistics_partial',
        'kwargs': {'cutoff': cutoff, 'delta': delta},
    }

    # Create a new task for the desired organizations
    info('Dispatching node-tasks')
    task = client.create_new_task(
        input_=input_,
        organization_ids=ids
    )

    # Wait for nodes to return results
    info('Waiting for results')
    task_id = task.get('id')
    task = client.get_task(task_id)
    while not task.get('complete'):
        task = client.get_task(task_id)
        info('Waiting for results')
        time.sleep(1)

    # Collecting results
    info('Obtaining results')
    results = client.get_results(task_id=task.get('id'))

    # Organising partial results, we do not perform aggregations as we need
    # the data per centre for the dashboard
    info('Master algorithm complete')
    info(f'Result: {results}')

    return results


def RPC_statistics_partial(data, cutoff, delta):
    """ TNM statistics for dashboard

    Parameters
    ----------
    data
        DataFrame with the TNM data
    cutoff
        Maximum number of days for the survival rate profile
    delta
        Number of days between the time points in the profile

    Returns
    -------
    results
        Dictionary with the partial result
    """
    info('Counting number of unique ids')
    organisation = data['centre'].unique()[0]
    nids = data['id'].nunique()

    info('Counting number of unique ids per stage')
    stages = data.groupby(['stage'])['id'].nunique().reset_index()

    info('Counting number of unique ids per vital status')
    vital_status = data.groupby(['vital_status'])['id'].nunique().reset_index()

    info('Getting survival rates')
    survival = survival_rate(data, cutoff, delta)

    return {
        'organisation': organisation,
        'nids': nids,
        'stages': stages.to_dict(),
        'vital_status': vital_status.to_dict(),
        'survival': survival
    }
