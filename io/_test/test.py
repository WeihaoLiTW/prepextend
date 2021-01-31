# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

import sys
sys.path.append(r'C:\Dropbox\Fork\bluex')

import logging
logging.basicConfig(filename = r'C:\Dropbox\Fork\bluex\prep_extension\io\_test\log.txt',
                    format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt = '%H:%M:%S',
                    level = logging.DEBUG # .DEBUG
                    )

# In[]:import

from prep_extension.io.api import ( 
        prep_read
        )

# In[]:

prep_path = r'C:\Dropbox\Fork\bluex\prep_extension\prep_read\_sample\prep_example.tfl'
prep_path = r'C:\One Drive\OneDrive - 維新網股份有限公司\Prep Flow Pool\Completed Port List\Completed Port List.tfl'
prep_path = r'C:\\One Drive\\OneDrive - 維新網股份有限公司\\Prep Flow Pool\Completed Port List\Completed Port List_Download.tfl'
prep_path = r'C:\One Drive\OneDrive - 維新網股份有限公司\Prep Flow Pool\Datamyne\Make_Contained_Input.tfl'
#prep_path = r'C:\\One Drive\\OneDrive - 維新網股份有限公司\\Prep Flow Pool\GreenX_Rate\GreenX_Rate.tfl'

prep = prep_read(prep_path)
flow = prep.flow

# In[]:
    
sources = prep.list_sources()

# In[]:
'''
nodes = flow['nodes']
connections = flow['connections']

node_id = '3c2d4acf-2746-4fca-b402-04694a6c8143'    
connection_id = nodes[node_id]['connectionId']


node = nodes[node_id]
connection = connections[connection_id]
connectionAttributes = check_node['connectionAttributes']
'''

