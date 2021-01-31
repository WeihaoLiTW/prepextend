# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

import os
from os.path import join
import sys
sys.path.append(r'C:\Dropbox\Fork\bluex')

import logging
log_file = r'C:\Dropbox\Fork\bluex\prep_extension\management\_test\log.txt'
from pandas.util import hash_pandas_object

try:
    os.remove(log_file)
except:
    pass

logging.basicConfig(filename = log_file,
                    format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt = '%H:%M:%S',
                    level = logging.DEBUG # .DEBUG
                    )

import pandas as pd


# In[]:import

from prep_extension.management.api import (
    flow_manage
    )

from prep_extension.io.api import ( 
        prep_read
        )

# In[]:

flow_management = flow_manage()
all_sources = flow_management.all_sources_with_hash


# In[]:

target_flows = pd.read_excel(r'C:\Dropbox\Fork\bluex\prep_extension\management\_test\sample_target_flows.xlsx')    

target_flows.flow_dir
