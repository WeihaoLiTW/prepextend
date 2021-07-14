# -*- coding: utf-8 -*-
"""
Created on Sun May  9 13:49:12 2021

@author: weiha
"""

from prepextend.io.api import flow_read
from prepextend.common.api import dict_hash
import pandas as pd
from copy import deepcopy
import logging as log
import ntpath


def _hash_sources(sources: list) -> list:

    sources_dp = deepcopy(sources)
    sources_hash = []
    for source in sources_dp:
        del source['baseType']
        source_hash = dict_hash(source)
        sources_hash.append(source_hash)

    return sources_hash


def _break_down_flows(all_sources, up_flows: list):

    # get the input_hash of up_flows
    df = all_sources.copy()
    df = df.loc[df.flow.isin(up_flows)]
    df = df.loc[df.baseType == 'input']
    input_hash = set(df.source_hash.tolist())

    # get the flows, where the output has the same hash
    df = all_sources.copy()
    df = df.loc[df.baseType == 'output']
    df = df.loc[df.source_hash.isin(input_hash)]
    down_flows = df['flow'].drop_duplicates().to_list()

    return down_flows


def _check_loop_flows(deep_nun, flow_nun, draft_flow_map):

    if deep_nun > flow_nun:  # check loop flows
        with pd.option_context('display.max_colwidth', -1):
            # for print full path
            raise Exception(f"There are some loop flows, please check"
                            f"\n"
                            f"{draft_flow_map.flow}"
                            )


def _convert(flows_roadmap) -> list:

    new_flows_roadmap = []
    for i in flows_roadmap.index.tolist():
        flow_file = flows_roadmap.loc[i].flow
        flow_dir, flow_name = ntpath.split(flow_file)

        flow_info = {'flow_file': flow_file,
                     'flow_file_dir': flow_dir,
                     'flow_file_name': flow_name
                     }

        new_flows_roadmap.append(flow_info)

    return new_flows_roadmap


def construct_sourcesDF(flows: list):

    # flows = depend_flows
    sources_df = pd.DataFrame()

    # flow = flows[0]
    for flow in flows:
        try:
            flow_info = flow_read(flow)
            sources = flow_info['inputs_outputs']

            df = pd.DataFrame(sources)
            df['flow'] = flow
            # + hash
            df.insert(0, 'source_hash',
                      _hash_sources(sources)
                      )
            # append
            sources_df = sources_df.append(df)
        except Exception:
            print(f"failed to read prep file: {flow}")

    return sources_df


def flows_roadmap(target_flows: list, depend_flows: list) -> list:

    # get all soruces
    all_sources = construct_sourcesDF(set(target_flows + depend_flows))

    # setting
    flow_nun = all_sources.flow.nunique()
    draft_flow_map = pd.DataFrame()
    up_flows = target_flows.copy()

    # make flow
    deep_nun = 0
    while len(up_flows) > 0:
        log.debug(f"up_flows: {up_flows}")
        down_flows = _break_down_flows(all_sources=all_sources,
                                       up_flows=up_flows
                                       )
        # append to whole map
        draft_flow_map = draft_flow_map.append(
            pd.DataFrame(up_flows, columns=['flow']),
            ignore_index=True
            )
        # reset the up_flows
        up_flows = down_flows.copy()
        log.debug(f"down_flows: {down_flows}")

        deep_nun += 1
        _check_loop_flows(deep_nun,
                          flow_nun,
                          draft_flow_map
                          )

    # remove duplicarte
    flows_roadmap = draft_flow_map.drop_duplicates(subset=['flow'],
                                                   keep='last',
                                                   ignore_index=True
                                                   )
    # sort
    flows_roadmap = flows_roadmap.iloc[::-1]
    flows_roadmap = flows_roadmap.reset_index(drop=True)

    # convert for better integrate with run api
    flows_roadmap = _convert(flows_roadmap)

    return flows_roadmap
