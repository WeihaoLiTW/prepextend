# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

import json
import os
from os.path import join
import datetime
from pandas import read_csv
from math import ceil

from prepextend.management._config.config import config_set
from prepextend.management._notify.api import send_msg
from prepextend.common.api import list_files
from prepextend.io.api import flow_read
from prepextend.run.api import flow_run
from prepextend.map.api import flows_roadmap
from prepextend.map.api import construct_sourcesDF as construct_sources
from prepextend.common.api import path_split

# In[]:


class flow_manage:

    def __init__(self,
                 general_config,
                 version_assigned=None
                 ):

        self._config = config_set(general_config,
                                  version_assigned
                                  )
        # grt required configs
        self._versions_and_prep_scripts = self._config.prep_scripts_4_version_assigned
        self._retry_times = self._config.retry_times
        self._default_prep_script = self._config.default_prep_script
        self._credentials_file_suffix = self._config.credentials_file_suffix
        self._check_file_tags = self._config.check_file_tags
        self._log_save_dir = self._config.log_save_dir
        self._flow_pool = self._config.flow_pool
        self._version_assigned = self._config.version_assigned
        self._notify_channels = self._config.notify_channels

    def _assign_prep_script_byconfig(self, flow_file: str) -> str:

        flow_dir, flow_name = path_split(flow_file)

        flows_defined_version = self._version_assigned
        default_prep_script = self._default_prep_script
        versions_and_prep_scripts = self._versions_and_prep_scripts

        # check version
        if flow_file in flows_defined_version.keys():
            # use custom setting if exist
            flow_version = flows_defined_version[flow_file]
            print(f"{flow_name} has defined version: {flow_version}")
            if flow_version in versions_and_prep_scripts.keys():
                prep_script = versions_and_prep_scripts[flow_version]
            else:
                prep_script = default_prep_script
                print("but can't find the the prep_script in the config,"
                      "so use default_prep_script")
        else:
            prep_script = default_prep_script
            print(f"{flow_name} has no defined version,"
                  " use default_prep_script")

        return prep_script

    def _credential_file_byconfig(self, flow_file: str) -> str:

        flow_file_dir, flow_file_name = path_split(flow_file)

        credential_name = (os.path.splitext(flow_file_name)[0]
                           + self._credentials_file_suffix
                           )

        credential_file = join(flow_file_dir, credential_name)

        if os.path.isfile(credential_file) is False:
            return None
        else:
            return credential_file

    def _save_log(self, run_result: dict, log_save_dir: str):

        class MyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, bytes):
                    return str(obj, encoding='utf-8', errors='ignore')
                return json.JSONEncoder.default(self, obj)

        start_time = run_result['start_time']
        start_f = datetime.datetime.fromtimestamp(
                    start_time).strftime('%Y-%m-%d-%H-%M-%S')

        run_mins = ceil(run_result['run_secs']/60)
        flow_name = run_result['flow_file_name']

        log_name = ('log_' + flow_name
                    + '_' + start_f
                    + '_' + str(run_mins)
                    + '.json')
        log_file = join(log_save_dir, log_name)

        # dump
        with open(log_file, "w", encoding='utf-8') as fp:
            json.dump(run_result, fp, cls=MyEncoder, sort_keys=False, indent=4)

    def _list_checkpoints(self, flow_file: str, check_file_tags: list) -> list:
        flow_info = flow_read(flow_file)
        sources = flow_info['inputs_outputs']

        check_files = []
        for source in sources:
            # get all csv outputs
            source_path = source['name']
            _, file_name = path_split(source_path)
            if source['baseType'] == 'output' and 'csv' in file_name:
                # only include file with tag
                if any(tag in file_name for tag in check_file_tags):
                    check_files.append(source_path)
        return check_files

    def list_flows(self, flow_suffix='.tfl') -> list:

        def _ignore(flow_path, ignore_tags):
            for tag in ignore_tags:
                if tag in flow_path:
                    return True
            return False

        if self._flow_pool is None:
            raise Exception("There is no flow pool setting in config")
        else:
            flow_pool_dir = self._flow_pool['pool_dir']
            ignore_tags = self._flow_pool['ignore_tags']
            _, _, files = list_files(flow_pool_dir)
            flows = []

            for file in files:
                if file.endswith(flow_suffix):
                    if ignore_tags is None:
                        flows.append(file)
                    elif _ignore(file, ignore_tags) is False:
                        flows.append(file)
            return flows

    def construct_sourcesDF(self):

        if self._flow_pool is None:
            raise Exception("There is no flow pool setting in config")
        else:
            flows = self.list_flows()
            all_sources = construct_sources(flows)

        return all_sources

    def flows_roadmap(self, target_flows, depend_flows=None) -> list:

        if depend_flows is None:
            if self._flow_pool is not None:
                depend_flows = self.list_flows()
            else:
                raise Exception("Either No depend flows OR"
                                "There is no flow pool setting in config")

        run_roadmap = flows_roadmap(target_flows=target_flows,
                                    depend_flows=depend_flows
                                    )

        return run_roadmap

    def check_checkpoints(self, flow_file) -> list:
        # set variables
        check_file_tags = self._check_file_tags

        # make list files folder path
        checkpoints = self._list_checkpoints(flow_file, check_file_tags)

        check_results = []
        if len(checkpoints) == 0:
            print(f"There is no checkpoint in the flow: {flow_file}")
        else:
            for checkpoint in checkpoints:
                checkpoint_content = read_csv(checkpoint, engine='python',
                                              encoding='utf-8-sig')
                # check
                result = checkpoint_content.shape[0] > 0
                # formated the check_result
                check_result = {'checkpoint': checkpoint,
                                'with issue': result
                                }
                check_results.append(check_result)

        return check_results

    def run_flow(self, flow_file: str) -> dict:

        max_try_times = 1 + int(self._retry_times)
        prep_script = self._assign_prep_script_byconfig(flow_file)
        credential_file = self._credential_file_byconfig(flow_file)
        check_file_tags = self._check_file_tags
        log_save_dir = self._log_save_dir

        # run
        run_results = []
        num_run = 1
        successfully_run = False
        while num_run <= max_try_times and successfully_run is False:
            run_result = flow_run(prep_script,
                                  flow_file,
                                  credential_file
                                  )
            # append info
            run_result['num_run'] = num_run
            run_result['max_try_times'] = max_try_times

            # update condition
            successfully_run = run_result['successfully_run']
            num_run += 1

            # notify run error
            if successfully_run is False:
                if self._notify_channels is not None:
                    send_msg(notify_channels=self._notify_channels,
                             msg_type='run_fail',
                             run_result=run_result
                             )
            # check checkpoints
            if successfully_run is True and check_file_tags is not None:
                check_results = self.check_checkpoints(flow_file)
                # append to run result
                run_result['check_checkpoints'] = check_results
                # get only checkpoints with issue
                checkpoints_warning = [x['checkpoint'] for x in check_results
                                       if x['with issue'] is True]

                # notify if there are some error files
                if len(checkpoints_warning) > 0:
                    send_msg(notify_channels=self._notify_channels,
                             msg_type='checkpoints_with_issue',
                             run_result=run_result,
                             checkpoints_warning=checkpoints_warning
                             )
            # save log
            if log_save_dir is not None:
                self._save_log(run_result, log_save_dir)

            # append result
            run_results.append(run_result)

        return run_results
