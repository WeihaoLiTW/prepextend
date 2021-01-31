# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:35:57 2020

@author: WEIHAO
"""


import os
from os.path import join
import sys
sys.path.append(r'C:\Dropbox\Fork\bluex')


# In[]:

import prep_extension    

# In[]:
    
flow_management = prep_extension.flow_manage.api.flow_manage()

all_sources = flow_management.all_sources_with_hash


target_flows = pd.read_excel(r'C:\Dropbox\Fork\bluex\prep_extension\flow_manage\_test\sample_target_flows.xlsx')  