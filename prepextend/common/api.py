# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

from os import walk
from os.path import join
import datetime
import json
import hashlib
from pandas import read_csv
from typing import Dict, Any
import ntpath

# In[]:


def dict_hash(dictionary: Dict[str, Any]) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)

    return dhash.hexdigest()


# In[]:

def time_utc_formated():
    time_presnet = datetime.datetime.now()
    time_now_formated = time_presnet.strftime('%Y %m %d %H %M %S')
    # format:https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    return time_now_formated

# In[]:


def path_split(path):
    head, tail = ntpath.split(path)
    # avoid error occur when only one layer
    return head, tail or ntpath.basename(head)


# In[]:

def list_files(folder_path):
    # include its sub-folders
    file_names = []
    file_dirs = []
    file_paths = []
    for root, dirs, files in walk(top=folder_path):
        for name in files:
            filepath = join(root, name)

            file_names.append(name)
            file_dirs.append(root)
            file_paths.append(filepath)

    return file_names, file_dirs, file_paths
    # format = series, dif vs list is serier has index
    # ref:https://discuss.analyticsvidhya.com/t/what-is-the-difference-between-pandas-series-and-python-lists/27373/2


# In[]: check_file = path\to\[your flow check name].csv

def check_fileWithRows(check_files: list):
    # make list files folder path

    error_files_name = []
    error_files_path = []
    for check_file in check_files:
        check_file_content = read_csv(check_file,
                                      engine='python',
                                      encoding='utf-8-sig')

        if check_file_content.shape[0] > 0:
            check_file_name = check_file.split('\\')[-1]

            error_files_name.append(check_file_name)
            error_files_path.append(check_file)

    return error_files_name, error_files_path
