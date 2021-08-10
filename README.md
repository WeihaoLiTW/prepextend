# prepextend
A toolset to expand the functionality for the Tableau Prep

## Key Features
1. Run Tableau Prep file through Python API.
2. Read the Tableau Prep file as a dict, which has an overview of all inputs and outputs.
3. Produce a flows execution sequential list from a group of the Tableau prep files with dependence.
4. Add-on features (require setting the config file):
   - 4.a. On top of feature 1, add retry when there is an error in running Tableau Prep file
   - 4.b. On top of feature 1, notify by Slack when running error.
   - 4.c. On top of feature 1, assign a specific version of Tableau Prep in a specific file to run.
   - 4.d. On top of feature 1, save running log.
   - 4.e. On top of feature 1, no more need to locate the credential file
   - 4.f. On top of feature 3, can assign a folder as a pool to the group of the Tableau prep files located.
   - 4.g. Can mark csv outputs as checkpoints and verify them after running file to secure the data quality.
   - 4.h. On top of feature 4-g, notify by Slack when getting issues in checkpoints.
	
### Note: 
- Featurs 2,3 are in the limited scope of connection test: 
   - Local file type: excel, csv, hyper
   - Non-Local: Postgres DB, Tableau Server  
   - If your Tableau Prep files contain some connection out of the above scope, might get error or incorrect result.

## Restriction
Currently, Windows OS support only.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install prepextend
```

## Usage

### 1. Run Tableau Prep file

```python
# returns runnning log 
from prepextend import flow_run

running_log = flow_run(prep_script = "[Tableau Prep Builder install location]\Tableau Prep Builder <version>\scripts",
                       flow_file = "path\to\[your flow file name].tfl", 
                       credential_file = "path\to\[your credential file name].json"
                       )
# eg. prep_script = "...\Tableau\Tableau Prep Builder 2020.2\scripts"
```

### 2. Read the Tableau Prep file
```python
# returns flow_info 
from prepextend import flow_read

flow_info = flow_read("path\to\[your flow file name].tfl")
```

### 3. Produce a flows execution sequential list with organized dependence.
```python
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
#  flow_map will be ['...\flow_1.tfl', '...\flow_2.tfl']
```

### 4. Set config for add-on features
```python
from prepextend import flow_manage

flow_management = flow_manage(general_config, version_assigned)
```

### 4.a ~ 4.e, 4.h Run flow with add-on features
```python
running_log = flow_management.run_flow("path\to\[your flow file name].tfl")
```

### 4.f When produce flow_map, apply the assign a folder as a pool to the group of the Tableau prep files located without input depend_flows
```python
target_flows = [
    '...\flow_3.tfl',
    ]

flow_map = flow_management.flows_roadmap(target_flows)
```