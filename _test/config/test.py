# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 15:41:06 2020

@author: WEIHAO
"""

import sys
sys.path.append(r'C:\Dropbox\Fork\bluex')

import logging
logging.basicConfig(filename = r'C:\Dropbox\Fork\bluex\prep_extension\_config\_test\log.txt',
                    format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt = '%H:%M:%S',
                    level = logging.DEBUG # .DEBUG
                    )

import json

# In[]:

from prep_extension._config.config import config_set

# In[]:
    
config = config_set()


# In[]:

config.log_save_path
    

# In[]:
f = open('config.json', 'r', encoding = 'utf-8')
config = f.read().replace('\\', '\\\\')
# can't decode if not replace.  https://www.itread01.com/content/1528896154.html
config = json.loads(config)
