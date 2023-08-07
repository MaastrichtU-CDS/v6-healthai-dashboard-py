# -*- coding: utf-8 -*-

""" Sample code to test the federated algorithm with a mock client
"""
import os
from vantage6.tools.mock_client import ClientMockProtocol


# Start mock client
data_dir = os.path.join(os.getcwd(), 'v6_healthai_dashboard_py', 'local')
client = ClientMockProtocol(
    datasets=[
        os.path.join(data_dir, 'data1.csv'),
        os.path.join(data_dir, 'data2.csv')
    ],
    module='v6_healthai_dashboard_py'
)

# Get mock organisations
organizations = client.get_organizations_in_my_collaboration()
print(organizations)
ids = [organization['id'] for organization in organizations]

# Check partial method
partial_task = client.create_new_task(
    input_={
        'method': 'statistics_partial',
        'kwargs': {
            'cutoff': 730,
            'delta': 30
        }
    },
    organization_ids=ids
)
results = client.get_results(partial_task.get('id'))
print(results)

# Check master method
master_task = client.create_new_task(
    input_={
        'master': True,
        'method': 'master',
        'kwargs': {
            'org_ids': [1],
            'cutoff': 730,
            'delta': 30
        }
    },
    organization_ids=[1]
)
results = client.get_results(master_task.get('id'))
print(results)
