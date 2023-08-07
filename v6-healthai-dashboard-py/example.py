# -*- coding: utf-8 -*-

import os
from vantage6.tools.mock_client import ClientMockProtocol


# Mock client
data_dir = os.path.join(os.getcwd(), 'v6-healthai-dashboard-py', 'local')
client = ClientMockProtocol(
    datasets=[
        os.path.join(data_dir, 'data1.csv'),
        os.path.join(data_dir, 'data2.csv')
    ],
    module='v6-healthai-dashboard-py'
)

# Check organisations
organizations = client.get_organizations_in_my_collaboration()
print(organizations)
ids = [organization['id'] for organization in organizations]

# Check partial method
task = client.create_new_task(
    input_={'method': 'statistics_partial'},
    organization_ids=ids
)
print(task)

results = client.get_results(task.get('id'))
print(results)

# Check master method
master_task = client.create_new_task(
    input_={'master': 1, 'method': 'master', 'kwargs': {'org_ids': [1]}},
    organization_ids=[1]
)
results = client.get_results(master_task.get('id'))
print(results)