# prepextend
A toolset to expand the functionality for the Tableau Prep

## Key Features
1. Run Tableau Prep file through Python API.
2. Read the Tableau Prep file as a dict, which has an overview of all inputs and outputs.
3. Produce a flows execution sequential list from a group of the Tableau prep files with dependence.
4. The below features needs to setup a config file:
   a. On top of feature 1, add retry when there is an error in running Tableau Prep file
   b. On top of feature 1, notify by Slack when running error.
   c. On top of feature 1, assign a specific version of Tableau Prep in a specific file to run.
   d. On top of feature 1, save running log.
   e. On top of feature 1, no more need to locate the credential file
   f. On top of feature 3, can assign a folder as a pool to the group of the Tableau prep files located.
   g. Can mark csv outputs as checkpoints and verify them after running file to secure the data quality.
   h. On top of feature 4-g, notify by Slack when getting issues in checkpoints.
	
Note: Featurs 2,3 are in the limited scope of connection test: 
	  Local file type: excel, csv, hyper
	  Non-Local: Postgres DB, Tableau Server  
	  If your Tableau Prep files contain some connection out of the above scope, might get error or incorrect result.

## Restriction
Currently, Windows OS support only.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install prepextend
```

## Usage

```python

# Features-1, returns runnning log 
from prepextend import flow_run

running_log = flow_run(prep_script = "[Tableau Prep Builder install location]\Tableau Prep Builder <version>\scripts",
                       flow_file = "path\to\[your flow file name].tfl", 
                       credential_file = "path\to\[your credential file name].json"
                       )
# eg. prep_script = "...\Tableau\Tableau Prep Builder 2020.2\scripts"


# Features-2, returns flow_info 
from prepextend import flow_read

flow_info = flow_read("path\to\[your flow file name].tfl")


# Features-3, return a sequential list with organized dependence.
from prepextend import flows_roadmap

depend_flows = ['...\flow_3.tfl', '...\flow_1.tfl', '...\flow_2.tfl']
# dependency = flow 1 -> flow 2 -> flow 3

target_flows = [
    '...\flow_3.tfl',
    ]

flow_map = flows_roadmap(target_flows, depend_flows)
# flow_map will be ['...\flow_1.tfl', '...\flow_2.tfl', '...\flow_3.tfl']

target_flows = [
    '...\flow_2.tfl',
    ]

flow_map = flows_roadmap(target_flows, depend_flows)
# flow_map = ['...\flow_1.tfl', '...\flow_2.tfl']


# Features-4, set config
from prepextend import flow_manage

flow_management = flow_manage(general_config, version_assigned)

# Features-4 a~e
running_log = flow_management.run_flow("path\to\[your flow file name].tfl")

# Features-4-f
target_flows = [
    '...\flow_3.tfl',
    ]

flow_map = flow_management.flows_roadmap(target_flows)
```