# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

import pandas as pd
import logging as log
from pandas.util import hash_pandas_object

from prepextend._config.config import config_set
from prepextend.io.api import prep_read
from prepextend.common.api import send_message_to_slack
from prepextend.common.api import list_files_path_in_folder

# In[]:

class flow_manage:
    
    def __init__(self, previous_all_sources = 'None'):
        
        self.config = config_set()
        self.flow_pool = self.config.flow_pool
        self.source_format = self.get_source_format()
        
        if previous_all_sources == 'None':
            self.all_sources_with_hash = self.get_all_sources_with_hash()
    
    
    def get_source_format(self):
        
        prep = prep_read()
        source_format = prep.source_format
        
        return source_format
        
    
    def notify_error_read_prep(self, failed_to_read_file):

        main_msg = f"[ERROR] Read Prep File Failed."
        sub_msgs_dict = {}
        sub_msgs_dict['title'] = [failed_to_read_file]
        sub_msgs_dict['title_link'] = [failed_to_read_file]

        send_message_to_slack(main_msg = main_msg, 
                              sub_msgs_dict = sub_msgs_dict, 
                              color_sub_msg = 'danger'
                              )        
    

    def notify_conflict_flows(self, conflict_flows):
        
        flow_dirs = conflict_flows.flow_dir
        flow_names = conflict_flows.flow_name
        sub_msg = [i + "\\" + j for i, j in zip(flow_dirs, flow_names)]

        main_msg = f"[ERROR] Conflict Flows."
        sub_msgs_dict = {}
        sub_msgs_dict['title'] = sub_msg 
        sub_msgs_dict['title_link'] = sub_msg

        send_message_to_slack(main_msg = main_msg, 
                              sub_msgs_dict = sub_msgs_dict, 
                              color_sub_msg = 'danger'
                              )   

        
    def ingnore(self, flow_path):
        
        for tag in self.config.ignore_tag:
            if tag in flow_path:
                return True
        
        return False
            
        
    def get_flow_list(self, flow_suffix = '.tfl'):
        
        file_names, file_dirs, file_paths = list_files_path_in_folder(self.flow_pool)
        
        flow_names_list = []
        flow_dirs_list = []
        flow_path_list = []
        
        for file_name, file_dir, file_path in zip(file_names, file_dirs, file_paths):
            
            if self.ingnore(file_path) == False and flow_suffix in file_name:
                
                flow_names_list.append(file_name)
                flow_dirs_list.append(file_dir)
                flow_path_list.append(file_path)
                                
        return flow_names_list, flow_dirs_list, flow_path_list
 
    
    def get_all_sources(self):
        
        all_sources = pd.DataFrame()
        
        flow_names_list, flow_dirs_list, flow_path_list = self.get_flow_list()
        for flow_name, flow_dir, flow_path in zip(flow_names_list, flow_dirs_list, flow_path_list):
            try:
                prep_infor = prep_read(flow_path)
                sources = prep_infor.list_sources()
                
                df = pd.DataFrame(sources) 
                df['flow_path'] = flow_path
                df['flow_dir'] = flow_dir.replace("\\\\","\\")
                df['flow_name'] = flow_name
                
                all_sources = all_sources.append(df)
            except:
                log.debug(f"failed to read prep file: {flow_path}")
                self.notify_error_read_prep(failed_to_read_file = flow_path)
             
        return all_sources


    def get_all_sources_with_hash(self):
            
        all_sources = self.get_all_sources()
        
        # get the scope of source infor
        source_format = list(self.source_format.keys())
        source_format.remove('baseType')
        
        # hash will be dif if the index is not the same
        sources_infro = all_sources[source_format].copy()
        sources_infro['f_index'] = '1'
        sources_infro = sources_infro.set_index('f_index')

        all_sources.insert(0, 'source_hash', 
                           hash_pandas_object(sources_infro).tolist()
                           )
        
        return all_sources


    def get_down_flows(self, up_flows):
                        
        df = self.all_sources_with_hash.copy()
        df = df.loc[ (df.flow_dir.isin(up_flows.flow_dir)) & (df.flow_name.isin(up_flows.flow_name)) ]
        df = df.loc[ df.baseType == 'input' ]
        
        input_hash = set(df.source_hash.tolist())
        
        df = self.all_sources_with_hash.copy() 
        df = df.loc[ df.baseType == 'output' ]
        df = df.loc[ df.source_hash.isin(input_hash) ]
        
        down_flows = df[ ['flow_dir', 'flow_name'] ].drop_duplicates()
        
        return down_flows


    def check_conflict(self):
        '''      
        the way to check conlict flow issue is to check the target flow with the flows processed 
        secondary round of down flow.
        
        example:    
        flow A -> flow B, Flow C -> flow A, flow D
        
        Then flow A will have a conlict flow issue.
        '''
        
        all_sources_with_hash = self.all_sources_with_hash.copy()
        
        target_flows = all_sources_with_hash[['flow_dir','flow_name']].drop_duplicates()
        # will have duplicated index if witthout reset index, and can't one by one for the loop
        target_flows = target_flows.reset_index(drop = True)

        all_conflict = pd.DataFrame()       
        for i in list(target_flows.index):
            target_flow = target_flows.loc[[i]]
            log.debug(f"Target Flows:{target_flow}")
            
            level = 0
            up_flows = target_flow
            while up_flows.shape[0] != 0 and level < 2:
                down_flows = self.get_down_flows(up_flows = up_flows)
                up_flows = down_flows.copy()
                level += 1
                log.debug(f"level:{level}")
                
            if level == 2:
                log.debug(f"down_flows:{down_flows}")
                # get conflict
                down_flows = down_flows[down_flows.flow_dir == target_flow.flow_dir[i]]
                down_flows = down_flows[down_flows.flow_name == target_flow.flow_name[i]]
                log.debug(f"conflict:{down_flows}")
            
                all_conflict = all_conflict.append(down_flows)
                
        if all_conflict.shape[0] > 0:
            self.notify_conflict_flows(conflict_flows = all_conflict)
            
        return all_conflict
    
        
    def generate_flow_map(self, target_flows):
        
        draft_flow_map = pd.DataFrame()
        up_flows = target_flows.copy()
        
        while up_flows.shape[0] != 0:         
            down_flows = self.get_down_flows(up_flows = up_flows)         
            # append to whole map
            draft_flow_map = draft_flow_map.append(up_flows)         
            # reset the up_flows
            up_flows = down_flows.copy()         
            log.debug(f"next_level_flow: {down_flows}")
        
        # remove duplicarte
        flow_map = draft_flow_map.drop_duplicates(subset = ['flow_dir', 'flow_name'], 
                                                  keep = 'last',
                                                  ignore_index = True
                                                  )
        # sort
        flow_map = flow_map.iloc[::-1]
        flow_map = flow_map.reset_index(drop = True)
        
        return flow_map 
        
        
        
        
        
        
        
        
        
        
    