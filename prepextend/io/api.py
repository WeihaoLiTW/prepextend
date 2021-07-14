# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 22:04:35 2020

@author: weihao
"""

from prepextend.io.read import (
        decode_flow
        )


def flow_read(flow_file):

    flow = decode_flow(flow_file)
    inputs_outputs = flow.list_sources()

    response = {
        'raw_structure': flow.flow,
        'inputs_outputs': inputs_outputs
        }

    return response
