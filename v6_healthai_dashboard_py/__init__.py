# -*- coding: utf-8 -*-

""" methods.py

This file contains all algorithm pieces that are executed on the nodes.
It is important to note that the master method is also triggered on a
node just the same as any other method.

When a return statement is reached the result is send to the central
server after encryption.
"""
import os
import sys
import time
import json
import pandas

from vantage6.tools.util import info, warn
from v6_healthai_dashboard_py.survival import survival_rate


def master(client, data, org_ids=None, cutoff=730, delta=30):
    """Master algorithm.

    The master algorithm is the chair of the Round Robin, which makes
    sure everyone waits for their turn to identify themselves.
    """

    # Get all organizations (ids) that are within the collaboration
    # FlaskIO knows the collaboration to which the container belongs
    # as this is encoded in the JWT (Bearer token)
    info('Collecting participating organizations')
    organizations = client.get_organizations_in_my_collaboration()
    ids = [organization.get('id') for organization in organizations \
           if not org_ids or organization.get('id') in org_ids]

    # The input for the algorithm is the same for all organizations
    # in this case
    info('Defining input parameters')
    input_ = {
        'method': 'statistics_partial',
        'kwargs': {'cutoff': cutoff, 'delta': delta},
    }

    # Create a new task for all organizations in the collaboration
    info('Dispatching node-tasks')
    task = client.create_new_task(
        input_=input_,
        organization_ids=ids
    )

    # Wait for node to return results. Instead of polling it is also
    # possible to subscribe to a websocket channel to get status
    # updates
    info('Waiting for results')
    task_id = task.get('id')
    task = client.get_task(task_id)
    while not task.get('complete'):
        task = client.get_task(task_id)
        info('Waiting for results')
        time.sleep(1)

    info('Obtaining results')
    results = client.get_results(task_id=task.get('id'))

    # Organising partial results
    info('Master algorithm complete')
    info(f'Result: %s' % results)

    return results

def RPC_statistics_partial(data, cutoff, delta):
    """ TNM statistics for dashboard
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