# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 10:34:37 2020

@author: WEIHAO
"""

import datetime
from os.path import join
import os
import subprocess
from math import ceil
import logging as log
from pandas import read_csv

from prepextend._config.config import config_set
from prepextend.common.api import time_utc_formated
from prepextend.common.api import send_message_to_slack
from prepextend.io.api import prep_read
    

class prep_run:
    
    def __init__(self, 
                 prepfile_folder_path, 
                 prepfile_name # No Filename Extension (.tfl)
                 ):
        
        self.folder_path = prepfile_folder_path
        self.file_name = prepfile_name

        self.config = config_set()
        
        self.prep_infor = prep_read(prep_path = join(self.folder_path, self.file_name + '.tfl') )
        self.sources = self.prep_infor.list_sources()
        
        self.prep_version = self.run_verison()
        self.credentials_file_name = self.credentials_file_name()
        self.prep_script_path = self.config.prep_script_path[ self.prep_version ]
    

    def notify_check_files_with_error(self):
        
        error_files_name, error_files_path = self.check_file_with_error()
        if len(error_files_name) > 0:
            main_msg = f"[Warning] Found Faulty Data in Tableau Prep Flow.  Flow Name: {self.file_name}" \
                       f"\n"\
                       f"{self.folder_path}"  
      
            # generate the sub_msgs for slack send msg
            sub_msgs_dict = {}
            sub_msgs_dict['title'] = error_files_name
            sub_msgs_dict['title_link'] = error_files_path
        
            send_message_to_slack(main_msg = main_msg, 
                                  sub_msgs_dict = sub_msgs_dict,
                                  color_sub_msg = 'warning',
                                  )        
            
               
    def notify_retry(self, retried_times):
        
        main_msg = f"[ERROR] Tableau Prep Flow Run Failed.  Retried Times: {retried_times}"\
                   f"\n"\
                   f"{self.folder_path}"
        sub_msgs_dict = {}
        sub_msgs_dict['title'] = [self.file_name]
        sub_msgs_dict['title_link'] = [join( self.folder_path, self.file_name)]

        send_message_to_slack(main_msg = main_msg, 
                              sub_msgs_dict = sub_msgs_dict, 
                              color_sub_msg = 'danger'
                              )

    
    def credentials_file_name(self):
        
        credentials_file_name = self.file_name + self.config.credentials_file_suffix
        log.debug(f"credentials:{credentials_file_name}")
        
        # check whether the credentials file exist, if yes, with it; if no, skip
        if os.path.isfile( join(self.folder_path, credentials_file_name) ):
            print(f"{self.file_name} is with credentials file")            
            return credentials_file_name
        else:
            print(f"{self.file_name} is without credentials file")
            log.debug('credentials:None')
            return 'None'

    
    def run_verison(self):
        
        try:
            # use custom setting if exist
            prep_version = self.config.prep_files_script_version[self.folder_path][self.file_name]
            print(f"{self.file_name} is using the Defined Version: {prep_version}")            
        except:
            prep_version = self.config.prep_last_verison
            print(f"{self.file_name} is using the latest Version: {prep_version}, no version defined in the file")
        
        log.debug(f"prep_version:{prep_version}")         
        return prep_version
        
   
    def cmd_win(self):                       
        # prepare the cmd which is sent to tableau prep script
        located_prep_bat = '"' + join(self.prep_script_path, 'tableau-prep-cli.bat') + '"'
        located_prep_file = ' -t ' + '"' + self.file_name + '.tfl' + '"'
        
        # cmd will be depend on whether there is a credential or not.
        if self.credentials_file_name != 'None':
            located_prep_credentials = ' -c ' + '"' + self.credentials_file_name +'"'
            cmd = located_prep_bat + located_prep_credentials + located_prep_file
        else:
            cmd = located_prep_bat + located_prep_file
        
        # for showing
        print(cmd) 
        log.debug(cmd)
         
        return cmd
    

    def run_prep_win(self):    
        # record start time
        start_time_4logname = time_utc_formated()
        start = datetime.datetime.now() 
        
        cmd = self.cmd_win()
        logs = []    
        # run prep by prep script
        process = subprocess.Popen(args = cmd,
                                   shell = True,
                                   stdout = subprocess.PIPE,
                                   stderr = subprocess.PIPE,
                                   cwd = self.folder_path # cd path
                                   )
        # save and showing log
        for line in process.stdout:
            logs.append(line)
            print(line)
        
        # save errcode
        errcode = process.returncode
        
        # record end time and processing time
        end = datetime.datetime.now() 
        processing_min = str( int( ceil( (end - start).total_seconds()/60))) # take ceiling min
    
        # save logs
        log_name = "\log_" + self.file_name + '_' + start_time_4logname + '_' + processing_min + '.txt'
        log_path = self.config.log_save_path + log_name
    
        # write way use wb+, please refer: https://blog.csdn.net/liuweiyuxiang/article/details/78182603
        with open( log_path , "wb+") as f:
            for line in logs:
                f.write(line)
        
        # show error if have
        if errcode is not None:
            raise Exception('cmd %s failed, see above for details', cmd)
        
        return logs


    def check_run_successful(self, logs, 
                             success_str = 'Finished running the flow successfully'
                             ):   
        # since the logs from process.stdout are bytes-like object, need to convert the str to bytes then can compare with.
        # any() refer: https://www.cnblogs.com/apple2016/p/5767453.html
        result = any( [success_str.encode() in list_item for list_item in logs])   
        # result -> True or False
      
        return result
 
    
    def list_check_file(self):
        
        check_files = []
        for source in self.sources:
            if source['baseType'] == 'output' and source['con_type'] == 'localfile':
                file_name = source['name'].split('\\')[-1]
                # only include csv file and with tag 
                if self.config.check_file_tag in file_name and 'csv' in file_name:
                    check_file = source['name']
                    check_files.append(check_file)
                    
        return check_files
                
    
    def check_file_with_error(self):       
        # make list files folder path
        check_files = self.list_check_file()
        
        error_files_name = []
        error_files_path = []
        for check_file in check_files:
            check_file_content = read_csv(check_file, engine='python', encoding='utf-8-sig')
            
            if check_file_content.shape[0] > 0:
                check_file_name = check_file.split('\\')[-1]
                
                error_files_name.append(check_file_name)
                error_files_path.append(check_file)      
                
        return error_files_name, error_files_path
        

    def run_prep_win_main(self):
        
        retried_times = 0
        
        while retried_times <= self.config.retry_max:
            logs = self.run_prep_win()
            if self.check_run_successful(logs) == False:
                self.notify_retry(retried_times)
                retried_times += 1                
            else:
                self.notify_check_files_with_error()
                break
