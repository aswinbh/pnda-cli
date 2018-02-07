#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2016 Cisco and/or its affiliates.
#   This software is licensed to you under the terms of the Apache License, Version 2.0
#   (the "License").
#   You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#   The code, technical concepts, and all information contained herein, are the property of
#   Cisco Technology, Inc.and/or its affiliated entities, under various laws including copyright,
#   international treaties, patent, and/or contract.
#   Any use of the material herein must be in accordance with the terms of the License.
#   All rights not expressly granted by the License are reserved.
#   Unless required by applicable law or agreed to separately in writing, software distributed
#   under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
#   ANY KIND, either express or implied.
#
#   Purpose: Utilities used by PNDA CLI to create PNDA

import os
import json
import time
import logging
import subprocess_to_log

class PNDAConfigException(Exception):
    pass

RUNFILE = None
def init_runfile(cluster):
    global RUNFILE
    RUNFILE = 'cli/logs/%s.%s.run' % (cluster, int(time.time()))

def to_runfile(pairs):
    '''
    Append arbitrary pairs to a JSON dict on disk from anywhere in the code
    '''
    mode = 'w' if not os.path.isfile(RUNFILE) else 'r'
    with open(RUNFILE, mode) as runfile:
        jrf = json.load(runfile) if mode == 'r' else {}
        jrf.update(pairs)
        json.dump(jrf, runfile)

MILLI_TIME = lambda: int(round(time.time() * 1000))

LOG_FILE_NAME = None
CONSOLE_LOGGER = None
FILE_LOGGER = None

def init_logging():
    global LOG_FILE_NAME
    global CONSOLE_LOGGER
    global FILE_LOGGER
    if LOG_FILE_NAME is None:
        LOG_FILE_NAME = 'logs/pnda-cli.%s.log' % time.time()
        logging.basicConfig(filename=LOG_FILE_NAME,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        log_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        FILE_LOGGER = logging.getLogger('everything')
        CONSOLE_LOGGER = logging.getLogger('CONSOLE_LOGGER')
        CONSOLE_LOGGER.addHandler(logging.StreamHandler())
        CONSOLE_LOGGER.handlers[0].setFormatter(log_formatter)

def scp(files, cluster, host):
    cmd = "scp -F cli/ssh_config-%s %s %s:%s" % (cluster, ' '.join(files), host, '/tmp')
    CONSOLE_LOGGER.debug(cmd)
    ret_val = subprocess_to_log.call(cmd.split(' '), FILE_LOGGER, host)
    if ret_val != 0:
        raise Exception("Error transferring files to new host %s via SCP. See debug log (%s) for details." % (host, LOG_FILE_NAME))

def ssh(cmds, cluster, host):
    cmd = "ssh -F cli/ssh_config-%s %s" % (cluster, host)
    parts = cmd.split(' ')
    parts.append(';'.join(cmds))
    CONSOLE_LOGGER.debug(json.dumps(parts))
    ret_val = subprocess_to_log.call(parts, FILE_LOGGER, host, scan_for_errors=[r'lost connection', r'\s*Failed:\s*[1-9].*'])
    if ret_val != 0:
        raise Exception("Error running ssh commands on host %s. See debug log (%s) for details." % (host, LOG_FILE_NAME))

if __name__ == "__main__":
    pass
