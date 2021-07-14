# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

from strictyaml import load


class config_set:

    def __init__(self,
                 general_config,
                 version_assigned
                 ):

        self.read_config(general_config)
        self.version_assigned = self.read_version_assigned(version_assigned)

    def load_yaml(self, yaml_path):

        content = open(yaml_path, 'r', encoding="utf-8").read()
        return load(content).data

    def read_config(self, general_config):

        general_config = self.load_yaml(general_config)
        input_items = general_config.keys()

        # required config + default value
        required_items = {'default_prep_script': None,
                          'retry_times': "1",
                          'credentials_file_suffix': "_Credentials.json"
                          }

        for r_item in required_items.keys():
            key = r_item
            if r_item in input_items:
                value = general_config[key]
            else:
                value = required_items[key]
                if value is None:
                    raise Exception(f"Lack required config: {key}")
            setattr(self, key, value)
            # ref:https://stackoverflow.com/questions/52099692/how-to-assign-self-attributes-in-a-class-in-a-for-loop/52099781

        # optional config
        optional_items = ['prep_scripts_4_version_assigned',
                          'log_save_dir',
                          'check_file_tags',
                          'notify_channels',
                          'flow_pool'
                          ]

        for o_item in optional_items:
            key = o_item
            if o_item in input_items:
                value = general_config[key]
            else:
                value = None
            setattr(self, key, value)

    def read_version_assigned(self, version_assigned):

        if version_assigned is None:
            return None
        else:
            return self.load_yaml(version_assigned)
