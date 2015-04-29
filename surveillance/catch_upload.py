# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import commands
import cStringIO
import time
import threading
import subprocess
import glob

import logging

logging.basicConfig(level=logging.DEBUG)

ENDPOINT="http://10.200.44.66:8080/auth/v1.0"
USERNAME="test:tester"
USERKEY="testing"
CONTAINER="videos"

UPLOAD_FILE = "*.avi"
LOCAL_DIR = "/home/pc/catch_video/videos/"
SHELL_DIR = '/root/catch_video/catch.sh'
# DOWNLOAD_AS = "aa"+"2"+".txt"
UPLOADING_INTERVAL = 5

def catch_video():
    stat = commands.getoutput("sh ~/catch_video/catch.sh")
    logging.debug('catch.sh...')


def upload(pathname):
    stat = commands.getoutput("swift -A " + ENDPOINT + " -U "+ USERNAME 
                + " -K " + USERKEY + " upload " + CONTAINER + " " + pathname)
                # + ' --object-name ' + filename)
    logging.debug('uploaded video: %s' % stat)
    print(stat)


def delete_uploaded(pathname):
    # stat = commands.getoutput("rm " + LOCAL_DIR + "*." + suffix)
    stat = commands.getoutput("rm " + pathname)
    logging.debug('deleted video: %s' % pathname)
    print(stat)


def videos2upload():
    """
    get all the videos in the path, remove the latest one from list
    """
    logging.debug('dir: %s' % LOCAL_DIR + UPLOAD_FILE)
    video_list = glob.glob(LOCAL_DIR + UPLOAD_FILE)
    logging.debug('before sort: %s' % video_list)
    video_list.sort()
    logging.debug('after sort: %s, len: %d' % (video_list, len(video_list)))
    video_list = video_list[0:len(video_list)-1]
    logging.debug('after cut: %s, len: %d' % (video_list, len(video_list)))
    return video_list


def keep_uploading():
    videos = videos2upload()
    for video in videos:
        upload(video)
        delete_uploaded(video)


def subfunc():
    print('threading %s running...' % threading.current_thread().name)
    # datain = raw_input('pleas input: ')

    print('threading %s ending...' % threading.current_thread().name)

def main():
    subprocess.Popen('shell ' + SHELL_DIR, shell=True)
    while True:
        print('start to upload...')
        keep_uploading()
        time.sleep(UPLOADING_INTERVAL)
    # logging.debug('videos: %s' % videos)
    # upload(LOCAL_DIR, UPLOAD_FILE)
    # delete_uploaded('mp4')


if __name__ == '__main__':
    main()