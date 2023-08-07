# Vantage6 algorithm to get TNM statistics

This algorithm was designed for the [vantage6](https://vantage6.ai/) 
architecture. It computes the following statistics:

- number of patients per centre
- number of patients per overall stage per centre
- number of patients per vital status per centre
- survival rate profile per centre

## Input data

The algorithm expects each data node to hold a `csv` with the following data 
and adhering to the following standard:

``` json
{
    'id': {
        'description': 'patient identifier',
        'type': 'string'
    },
    'stage': {
        'description': 'patient overall stage',
        'type': 'categorical'
    }, 
    'date_of_diagnosis': {
        'description': 'date the patient was diagnosed',
        'type': 'string',
        'format': '%Y-%m-%d'
    },
    'date_of_fu': {
        'description': 'date the patient had the last follow up visit',
        'type': 'string',
        'format': '%Y-%m-%d'
    },
    'vital_status': {
        'description': 'patient vital status',
        'type': 'categorical',
        'values': ['alive', 'dead']
    },
    'centre': {
        'description': 'hospital identifier',
        'type': 'string'
    } 
}
```

The files `data1.csv` and `data2.csv` in the directory
`v6_healthai_dashboard_py/local` are examples.

## Using the algorithm

Below you can see an example of how to run the algorithm:

``` python
import time
from vantage6.client import Client

# Initialise the client
client = Client('http://127.0.0.1', 5000, '/api')
client.authenticate('username', 'password')
client.setup_encryption(None)

# Define algorithm input
input_ = {
    'method': 'master',
    'master': True,
    'kwargs': {
        'org_ids': [2, 3],  # organisations to compute statistics
        'cutoff': 730,      # cutoff days for survival rate profile
        'delta': 30         # interval between days in the survival rate profile
    }
}

# Send the task to the central server
task = client.task.create(
    collaboration=1,
    organizations=[2, 3],
    name='v6-healthai-dashboard-py',
    image='aiaragomes/v6-healthai-dashboard-py:latest',
    description='get tnm statistics',
    input=input_,
    data_format='json'
)

# Retrieve the results
task_info = client.task.get(task['id'], include_results=True)
while not task_info.get('complete'):
    task_info = client.task.get(task['id'], include_results=True)
    time.sleep(1)
result_info = client.result.list(task=task_info['id'])
results = result_info['data'][0]['result']
```

## Testing locally

If you wish to test the algorithm locally, you can create a Python virtual 
environment, using your favourite method, and do the following:

``` bash
source .venv/bin/activate
pip install -e .
python v6_healthai_dashboard_py/example.py
```

The algorithm was developed and tested with Python 3.10.

## Acknowledgments

This project was financially supported by the
[AiNed foundation](https://ained.nl/over-ained/).
