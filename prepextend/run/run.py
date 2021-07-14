# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 10:34:37 2020

@author: WEIHAO
"""

from os.path import join
import subprocess
import time
from math import ceil
from prepextend.common.api import path_split
import platform

'''
examples of inputs
# prep_script_path = [Tableau Prep Builder install location]\Tableau Prep Builder <version>\scripts
# flow_file = path\\to\\[your flow file name].tfl
# credential = \\server\\path\\[your credential file name].json

flow_file_name = [your flow file name].tfl
credential_name = [your credential file name].json
flow_file_dir = path\to\
'''


def _cmd_win(prep_script: str,
             flow_file: str,
             credential_file: str = None
             ) -> str:

    # prepare the cmd which is sent to tableau prep script
    located_prep_bat = '"' + join(prep_script, 'tableau-prep-cli.bat') + '"'
    located_prep_file = ' -t ' + '"' + flow_file + '"'

    # cmd will be depend on whether there is a credential or not.
    if credential_file is not None:
        located_prep_credentials = ' -c ' + '"' + credential_file + '"'
        cmd = located_prep_bat + located_prep_credentials + located_prep_file
    else:
        cmd = located_prep_bat + located_prep_file

    # for showing
    print(cmd)

    return cmd


def _whether_run_successful(
        logs: list,
        ) -> bool:

    _success_str = 'Finished running the flow successfully'
    IsSuccess = any([_success_str.encode() in list_item for list_item in logs])

    return IsSuccess


def run(prep_script: str,
        flow_file: str,
        credential_file: str = None
        ) -> dict:

    flow_file_dir, flow_file_name = path_split(flow_file)

    os_type = platform.system()
    if os_type == 'Windows':
        cmd = _cmd_win(prep_script, flow_file, credential_file)
    else:
        raise Exception(f"Sorry, Currently We Can't Support Your OS:{os_type}")

    # run prep by prep script
    start = int(time.time())

    process = subprocess.Popen(args=cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=flow_file_dir  # means cd path
                               )
    # save log
    logs = []
    for line in process.stdout:
        logs.append(line)
        print(line)

    # errcode
    errcode = process.returncode
    # show error if have
    if errcode is not None:
        raise Exception('cmd %s failed, see above for details', cmd)
    end = int(time.time())

    # produce response
    response = {'prep_script': prep_script,
                'flow_file': flow_file,
                'flow_file_dir': flow_file_dir,
                'flow_file_name': flow_file_name,
                'credential_file': credential_file,
                'os_type': os_type,
                'successfully_run': _whether_run_successful(logs),
                'start_time': start,
                'end_time': end,
                'run_secs': (end - start),
                'log': logs
                }

    return response
