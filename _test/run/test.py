# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

import sys
sys.path.append(r'C:\Dropbox\Fork\bluex')

import logging
logging.basicConfig(filename = r'C:\Dropbox\Fork\bluex\prep_extension\run\_test\log.txt',
                    format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt = '%H:%M:%S',
                    level = logging.DEBUG # .DEBUG
                    )

# In[]:import

import prep_extension.run.api as run

# In[]:

prepfile_folder_paths = [r'C:\Dropbox\Fork\bluex\prep_extension\prep_read\_sample',
                         r'C:\One Drive\OneDrive - 維新網股份有限公司\Schedule Flow\test_file'
                         ]

prepfile_names = ['prep_example',
                  'test_flow_with_error'
                  ]

# In[]: run_specify

i = 1
prep = run.prep_run(prepfile_folder_path = prepfile_folder_paths[i],
                    prepfile_name = prepfile_names[i]
                    ) 
prep.run_prep_main_win()


# In[]: run_all

for i in range(0,len(prepfile_folder_paths)):
    prep = run.prep_run(prepfile_folder_path = prepfile_folder_paths[i],
                        prepfile_name = prepfile_names[i]
                        ) 
    prep.run_prep_main_win()
