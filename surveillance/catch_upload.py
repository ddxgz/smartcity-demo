# -*- coding: utf-8 -*-
# didn't used
import cStringIO
import threading
import glob

from __future__ import absolute_import, division, print_function
import commands
import os, signal, subprocess, time
import logging

from six.moves import configparser

import swiftclient

logging.basicConfig(level=logging.DEBUG)

ENDPOINT="http://10.200.44.66:8080/auth/v1.0"
USERNAME="test:tester"
USERKEY="testing"
AUTH_VERSION="1"
CONTAINER="videos"

UPLOAD_FILE = "*.avi"
LOCAL_DIR = "/root/catch_video/videos/"
SHELL_DIR = '/root/catch_video/catch.sh'
# DOWNLOAD_AS = "aa"+"2"+".txt"
UPLOADING_INTERVAL = 6
VIDEOS2STOP = 3
THRESHOLD_CONTAINER = 40

def catch_video():
    stat = commands.getoutput("sh /root/catch_video/catch.sh")
    logging.debug('catch.sh...')


def upload(pathname):
    stat = commands.getoutput("swift -A " + ENDPOINT + " -U "+ USERNAME
                + " -K " + USERKEY + " upload " + CONTAINER + " " + pathname)
                # + ' --object-name ' + filename)
    logging.debug('uploaded video: %s' % stat)
    # print(stat)


def swift_upload(swift_conn, pathname):
    logging.debug('swift_conn uploading video: %s' % pathname)
    file = open(pathname)
    swift_conn.put_object(CONTAINER, pathname[-19:], file)
    # swift_conn.put_object(CONTAINER, pathname, file)
    logging.debug('swift_conn after uploading video: %s' % pathname)


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


def keep_uploading(swift_conn):
    videos = videos2upload()
    for video in videos:
        # upload(video)
        swift_upload(swift_conn, video)
        delete_uploaded(video)


def delete_excessive_objects(threshold):
    """
    just for demo
    get the number of objects in container, if it's beyond threshold, then
    delete all the container.
    """
    logging.debug('objects num before delete: not implemented')


def subfunc():
    print('threading %s running...' % threading.current_thread().name)
    # datain = raw_input('pleas input: ')

    print('threading %s ending...' % threading.current_thread().name)


def main():
    conn = swiftclient.Connection(ENDPOINT, USERNAME, USERKEY,
        auth_version=AUTH_VERSION)
    # account_head = conn.head_account()
    # check if container exists, create one if not
    conn.put_container(CONTAINER)
    logging.debug('created container...')
    # child_catch = subprocess.Popen('sh ' + SHELL_DIR, shell=True,
    #     preexec_fn=os.setsid)
    child_catch = subprocess.Popen('exec sh ' + SHELL_DIR, shell=True)
    logging.debug('child_catch pid: %s starting...' % child_catch.pid)
    cnt = 1
    while True:
        print('start to upload...')
        keep_uploading(conn)
        delete_excessive_objects(THRESHOLD_CONTAINER)
        time.sleep(UPLOADING_INTERVAL)
        cnt += 1
        logging.debug('########## cnt: %d ' % cnt)
        if cnt > VIDEOS2STOP + 1:
            break
    logging.debug('stop uploading...')
    # child_catch.terminate()
    ## cannot use popenobj.kill() to kill child, it will just kill the shell
    ## need to put exec in Popen before cmd
    # child_catch.kill()
    # child_catch.wait()
    time.sleep(1)
    child_catch.kill()
    # os.killpg(child_catch.pid, signal.SIGTERM)
    logging.debug('child_catch stop...')

    # upload(LOCAL_DIR, UPLOAD_FILE)
    # delete_uploaded('mp4')


if __name__ == '__main__':
    main()
