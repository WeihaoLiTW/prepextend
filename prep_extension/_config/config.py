# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

import json
from os.path import join
import logging as log
import pathlib

class config_set:
        
    def __init__(self):
        
        self.config_dicr = self.config_dicr()
        self.read_config()
        self.read_custom_prep_versions()
        
        self.prep_last_verison = self.prep_last_verison()
        
        
    def config_dicr(self):
        
        this_file_dir = pathlib.Path(__file__).parent.absolute()
        config_locate = join(this_file_dir, "../../_config_prep_extension")
        
        return config_locate
        
        
    def read_config(self):
        
        log.debug(f"config_dir: {self.config_dicr}, config_file_path: {join(self.config_dicr, 'config.json')}")
        f = open( join(self.config_dicr, 'config.json'), 'r', encoding = 'utf-8')
        config = f.read().replace('\\', '\\\\')
        # can't decode if not replace.  https://www.itread01.com/content/1528896154.html
        config = json.loads(config)
        
        self.log_save_path = config['log_save_path']
        self.prep_script_path = config['prep_script_path']
        self.retry_max = config['retry_max']
        self.credentials_file_suffix = config['credentials_file_suffix']
        self.run_self_suffix = config['run_self_suffix']
        self.check_file_tag = config['check_file_tag']    
        self.slack_webhook_url = config['slack_webhook_url']
        self.notify_slack_channel = config['notify_slack_channel']
        self.notify_sender_name = config['notify_sender_name']
        self.flow_pool = config['flow_pool']
        self.ignore_tag = config['ignore_tag']
        

    def read_custom_prep_versions(self):

        log.debug(f"config_dir: {self.config_dicr}, config_file_path: {join(self.config_dicr, 'prep_files_script_version.json')}")        
        v = open( join(self.config_dicr, 'prep_files_script_version.json'), 'r', encoding = 'utf-8')
        prep_files_script_version = v.read().replace('\\', '\\\\')
        self.prep_files_script_version = json.loads(prep_files_script_version)
        

    def prep_last_verison(self):
     
        last_verison = list(self.prep_script_path)[-1]
     
        return last_verison     
