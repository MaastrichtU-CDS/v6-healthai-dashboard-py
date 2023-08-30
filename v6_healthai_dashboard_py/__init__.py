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
    final_results
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
    names = [organization.get('name') for organization in organizations
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
    # TODO: how to get centre name from v6 client?
    info('Master algorithm complete')
    final_results = []
    for i, result in enumerate(results):
        if not result['organisation']:
            result['organisation'] = f'Centre {i}'
        final_results.append(result)

    return final_results


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
    # Initialising results dictionary
    results = {'logs': ''}

    info('Getting centre name')
    column = 'centre'
    if column in data.columns:
        centre = data[column].unique()[0]
        results['organisation'] = centre
    else:
        results['logs'] += f'Column {column} not found in the data\n'

    info('Counting number of unique ids')
    column = 'id'
    if column in data.columns:
        nids = data[column].nunique()
        results['nids'] = nids
    else:
        results['logs'] += f'Column {column} not found in the data\n'

    info('Counting number of unique ids per stage')
    column = 'stage'
    if column in data.columns:
        data[column] = data[column].str.upper()
        stages = data.groupby([column])['id'].nunique().reset_index()
        results[column] = stages.to_dict()
    else:
        results['logs'] += f'Column {column} not found in the data'

    info('Counting number of unique ids per vital status')
    column = 'vital_status'
    if column in data.columns:
        vital_status = data.groupby([column])['id'].nunique().reset_index()
        results[column] = vital_status.to_dict()
    else:
        results['logs'] += f'Column {column} not found in the data'

    info('Getting survival rates')
    columns = ['date_of_diagnosis', 'date_of_fu']
    if (columns[0] in data.columns) and (columns[1] in data.columns):
        survival = survival_rate(data, cutoff, delta)
        results['survival'] = survival
    else:
        results['logs'] += \
            f'Columns {columns[0]} and/or {columns[1]} not found in the data'

    return results
