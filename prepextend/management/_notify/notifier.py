# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:35:57 2020

@author: WEIHAO
"""
import requests
import json


def _send_message_to_slack(webhook_url: str,
                           main_msg: str,
                           sub_msg_titles: list,
                           color_sub_msg: str,
                           ):

    # generate attachements
    attachments = []

    for sub_title in sub_msg_titles:
        attachment = {"color": color_sub_msg,
                      "title": sub_title
                      }
        attachments.append(attachment)

    # generate msg to slack api
    payload = {
        "text": main_msg,
        "attachments": attachments
        }

    # post to slack api
    response = requests.post(
        webhook_url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
        )


def _msg_run_fail(channel_name: str, run_result: dict) -> dict:

    msg = {}
    flow_file = run_result['flow_file']
    num_run = run_result['num_run']
    max_try_times = run_result['max_try_times']

    # generate msg for slack
    if channel_name == 'slack':
        if num_run < max_try_times:
            level = 'warning'
        else:
            level = 'danger'
        # main msg
        msg['main_msg'] = (f"[{level.upper()}] Tableau Prep Run Flow Failed. "
                           f"Run Times: {num_run}/{max_try_times}"
                           )
        # sub meg
        sub_msg = {}
        sub_msg['titles'] = [flow_file]
        sub_msg['color'] = level
        msg['sub_msg'] = sub_msg

    return msg


def _msg_checkpoints_with_issue(channel_name: str,
                                run_result: dict,
                                checkpoints_warning: list
                                ) -> dict:

    msg = {}
    flow_file = run_result['flow_file']

    # generate msg for slack
    if channel_name == 'slack':
        level = 'warning'
        # main msg
        msg['main_msg'] = (f"[{level.upper()}] Tableau Prep "
                           "Detect Some Issues in Checkpoints"
                           f"\n Flow: {flow_file}"
                           )
        # sub meg
        sub_msg = {}
        sub_msg['titles'] = checkpoints_warning
        sub_msg['color'] = level
        msg['sub_msg'] = sub_msg

    return msg


def send_msg(notify_channels: list, msg_type: str, run_result: dict,
             checkpoints_warning: list = None
             ):

    for channel in notify_channels:
        channel_name = channel['name']

        # produce msg
        if msg_type == 'run_fail':
            msg = _msg_run_fail(channel_name,
                                run_result
                                )
        if msg_type == 'checkpoints_with_issue':
            msg = _msg_checkpoints_with_issue(channel_name,
                                              run_result,
                                              checkpoints_warning
                                              )
        # send msg
        if channel_name == 'slack':
            webhook_url = channel['webhook_url']
            main_msg = msg['main_msg']
            sub_msg_titles = msg['sub_msg']['titles']
            color_sub_msg = msg['sub_msg']['color']

            _send_message_to_slack(webhook_url,
                                   main_msg,
                                   sub_msg_titles,
                                   color_sub_msg
                                   )
