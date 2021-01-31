# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

from os import walk
from os.path import join
import datetime #for time stamp
import requests
import json

from prep_extension._config.config import config_set


config = config_set()


def time_utc_formated():
    time_presnet = datetime.datetime.now()  
    time_now_formated = time_presnet.strftime('%Y %m %d %H %M %S')
    # format: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
      
    return time_now_formated


def list_files_path_in_folder(folder_path):
    # include its sub-folders
    file_names = []
    file_dirs = []
    file_paths = []
    for root, dirs, files in walk(top = folder_path):
        for name in files:
            filepath = join(root, name)
            
            file_names.append(name)
            file_dirs.append(root)
            file_paths.append(filepath)
      
    return file_names, file_dirs, file_paths
    # format = series, dif vs list is serier has index. ref: https://discuss.analyticsvidhya.com/t/what-is-the-difference-between-pandas-series-and-python-lists/27373/2


def send_message_to_slack(main_msg, 
                          sub_msgs_dict = 'None', 
                          color_sub_msg = 'None',
                          webhook_url = config.slack_webhook_url,
                          channel = config.notify_slack_channel, 
                          sender_name = config.notify_sender_name
                          ):

    # generate attachements
    attachments = []

    if sub_msgs_dict != 'None':
        for title, title_link in zip(sub_msgs_dict['title'], sub_msgs_dict['title_link']):
            attachment = {"color":color_sub_msg,
                          "title":title,
                          "title_link":title_link
                          }
            attachments.append(attachment)
  
    # generate msg to slack api  
    payload = {
        "channel" : channel,
        "username" : sender_name,
        "text":main_msg,
        "attachments": attachments
        }
  
    # post to slack api
    response = requests.post(
        webhook_url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
        )

