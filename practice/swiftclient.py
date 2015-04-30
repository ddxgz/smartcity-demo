# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import commands
import cStringIO
import time
import threading
import subprocess
import glob
import logging
import json

from six.moves import configparser

import swiftclient

logging.basicConfig(level=logging.DEBUG)

ENDPOINT="http://10.200.44.66:8080/auth/v1.0"
USERNAME="test:tester"
USERKEY="testing"
AUTH_VERSION="1"
CONTAINER="videos"

UPLOAD_FILE = "*.avi"
LOCAL_DIR = "/home/pc/catch_video/videos/"
OBJ = "/home/pc/catch_video/videos/test.mp4"
SHELL_DIR = '/root/catch_video/catch.sh'
# DOWNLOAD_AS = "aa"+"2"+".txt"
UPLOADING_INTERVAL = 6


def main():
    conn = swiftclient.Connection(ENDPOINT, USERNAME, USERKEY,
        auth_version=AUTH_VERSION)
    account_head = conn.head_account()
    #logging.debug('head account: %s' % account_head)
    try:
        econtainer_head = conn.head_container('test1')
        logging.debug('head econtainer: %s' % econtainer_head)
        print('head container: %s' % json.dumps(econtainer_head, sort_keys=True, indent=4))
    except:
        logging.debug('in except')
        conn.put_container("test1")
    else:
        logging.debug('in else')
    econtainer_head = conn.head_container('videos')
    logging.debug('head econtainer: %s' % econtainer_head)
    print('head container: %s' % json.dumps(econtainer_head, sort_keys=True, indent=4))
    logging.debug('objects count: %s' % econtainer_head['x-container-object-count'])
    obj = b'42' * 10
    fileobj = open(OBJ)
   # conn.put_object("contest1", "objtest1", OBJ)

main()
