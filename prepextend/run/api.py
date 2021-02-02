# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 15:33:08 2019

@author: WEIHAO
"""

from prepextend._config.config import config_set
from prepextend.run.run_prep import prep_run

config = config_set()

def run_prep_self_win(prepfile_folder_path, 
                      py_file_name
                      ):
    # generate file name   
    prepfile_name = py_file_name.replace(config.run_self_suffix +'.py', '') # remove run_self_suffix.py     
    # run prep
    prep = prep_run(prepfile_folder_path = prepfile_folder_path,
                    prepfile_name = prepfile_name
                    ) 
    prep.run_prep_win_main()