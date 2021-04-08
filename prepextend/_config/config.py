# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

import json
from os.path import join
import logging as log
import pathlib
from prepextend_config import general_config, version_assigned

class config_set:
        
    def __init__(self, 
                 general_config = general_config, 
                 version_assigned = version_assigned
                 ):
        
        self.config = general_config
        self.version_assigned = version_assigned
        
        self.read_config()
        self.read_version_assigned()
        
        self.prep_last_verison = self.prep_last_verison()
        
    
    def read_config(self):
        
        config = self.config
        
        self.log_save_path = config['log_save_path']
        self.prep_script_path = config['prep_script_path']
        self.retry_max = config['retry_max']
        self.credentials_file_suffix = config['credentials_file_suffix']
        self.check_file_tag = config['check_file_tag']    
        self.slack_webhook_url = config['slack_webhook_url']
        self.flow_pool = config['flow_pool']
        self.ignore_tag = config['ignore_tag']
        

    def read_version_assigned(self):
        
        self.prep_files_script_version = self.version_assigned
        

    def prep_last_verison(self):
     
        last_verison = list(self.prep_script_path)[-1]
     
        return last_verison     
