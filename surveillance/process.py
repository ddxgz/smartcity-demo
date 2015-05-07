# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import commands
import os, signal, subprocess, time
import glob
import json
import logging
import functools
import threading

from six.moves import configparser

import swiftclient
import videoedit
from utils import funclogger, time2Stamp, stamp2Time

logging.basicConfig(level=logging.DEBUG)

#ENDPOINT="http://10.200.44.66:8080/auth/v1.0"
#USERNAME="test:tester"
#USERKEY="testing"
#AUTH_VERSION="1"
# CONTAINER="videos"
# UPLOAD_FILE = "*.avi"
# LOCAL_DIR = "/root/catch_video/videos/"
# SHELL_DIR = '/root/catch_video/catch.sh'
# DOWNLOAD_AS = "aa"+"2"+".txt"
# UPLOADING_INTERVAL = 6
# VIDEOS2STOP = 3
# THRESHOLD_CONTAINER = 40


class Config(object):
    def __init__(self, conf_file=None):
        if conf_file:
            self.config_file = conf_file
            self._get_config(specified=True)
        else:
            self._get_config()

    def _get_config(self, specified=False):
        if specified is True:
            config_file = self.config_file
        else:
            config_file = os.environ.get('SWIFTCLIENT_CONFIG_FILE',
                                     './swiftclient.conf')
        config = configparser.SafeConfigParser({'auth_version': '1'})
        config.read(config_file)
        if config.has_section('swiftconf'):
            auth_host = config.get('swiftconf', 'auth_host')
            auth_port = config.getint('swiftconf', 'auth_port')
            auth_ssl = config.getboolean('swiftconf', 'auth_ssl')
            auth_prefix = config.get('swiftconf', 'auth_prefix')
            self.auth_version = config.get('swiftconf', 'auth_version')
            self.account = config.get('swiftconf', 'account')
            self.username = config.get('swiftconf', 'username')
            self.password = config.get('swiftconf', 'password')
            self.auth_url = ""
            if auth_ssl:
                self.auth_url += "https://"
            else:
                self.auth_url += "http://"
            self.auth_url += "%s:%s%s" % (auth_host, auth_port, auth_prefix)
            if self.auth_version == "1":
                self.auth_url += 'v1.0'
            self.account_username = "%s:%s" % (self.account, self.username)
        else:
            self.skip_tests = True
        if config.has_section('catchconf'):
            self.container_video = config.get('catchconf', 'container_video')
            self.video_dir = config.get('catchconf', 'video_dir')
            self.shell_dir = config.get('catchconf', 'shell_dir')
            self.upload_file = config.get('catchconf', 'upload_file')
            uploading_interval = config.get('catchconf',
                                                 'uploading_interval')
            loopcount = config.get('catchconf', 'loopcount')
            threshold_container = config.get('catchconf',
                                                  'threshold_container')
            self.uploading_interval = int(uploading_interval)
            self.loopcount = int(loopcount)
            self.threshold_container = int(threshold_container)
            self.upload_dir = config.get('catchconf', 'upload_dir')
            wait_for_video_sec = config.get('catchconf',
                                                  'wait_for_video_sec')
            self.wait_for_video_sec = int(wait_for_video_sec)

        if config.has_section('devsetting'):
            no_catch = config.get('devsetting', 'no_catch')
            if no_catch is '0':
                self.no_catch = 0
            else:
                self.no_catch = 1
            auto_rename = config.get('devsetting', 'auto_rename')
            if auto_rename is '0':
                self.auto_rename = 0
            else:
                self.auto_rename = 1


@funclogger('--------auto_rename---------')
def rename(pathname):
    newname = pathname[:len(pathname)-14] + str(time.time())[0:10] + pathname[-4:]
    logging.info('rename to newname: %s' % newname)
    os.rename(pathname, newname)

## not used
# def catch_video():
#     stat = commands.getoutput("sh /root/catch_video/catch.sh")
#     logging.debug('catch.sh...')

## not used
# def upload(pathname, conf):
#     stat = commands.getoutput("swift -A " + conf.auth_url + " -U "+
#                               conf.account_username
#                 + " -K " + conf.password + " upload " + conf.container_video +
#                               " " + pathname)
#                 # + ' --object-name ' + filename)
#     logging.debug('uploaded video: %s' % stat)
#     # print(stat)

@funclogger('-------swift_upload-------')
def swift_upload(swift_conn, conf):
    videos = videos2upload(conf)
    logging.info('111 videos: %s ' % videos)
    if not videos or len(videos) is 0:
        logging.info('no video can be uploaded, wait: %s seconds' % 
            conf.uploading_interval)
        time.sleep(conf.uploading_interval)
        videos = videos2upload(conf)
    logging.info('videos: %s ' % videos)
    for video in videos:
        # upload(video)
        # swift_upload(swift_conn, video)
        logging.debug('swift_conn uploading video: %s' % video)
        file = open(video)
        swift_conn.put_object(conf.container_video, video[-19:], file)
        # swift_conn.put_object(CONTAINER, pathname, file)
        logging.debug('swift_conn after uploading video: %s' % video)
        if conf.auto_rename:
            time.sleep(1)
            rename(video)
        else:
            delete_uploaded(video)


@funclogger('--------delete_uploaded---------')
def delete_uploaded(pathname):
    # stat = commands.getoutput("rm " + LOCAL_DIR + "*." + suffix)
    # instead of os.remove()
    stat = commands.getoutput("rm " + pathname)
    logging.debug('deleted video: %s' % pathname)
    print(stat)


# @funclogger('--------videos2upload---------')
def videos2upload(conf):
    """
    get all the videos in the path, remove the latest one from list
    """
    logging.debug('dir: %s' % conf.video_dir + conf.upload_file)
    video_list = glob.glob(conf.video_dir + conf.upload_file)
    logging.debug('before sort: %s' % video_list)
    video_list.sort()
    logging.debug('after sort: %s, len: %d' % (video_list, len(video_list)))
    video_list = video_list[0:len(video_list)-1]
    logging.debug('after cut: %s, len: %d' % (video_list, len(video_list)))
    return video_list


def delete_stored(swift_conn):
    """
    get objects stored in swift,
    find out videos in local to delete.
    """
    logging.debug('delete objects have stored in swift: not implemented')
    # delete what in keep_uploading()


def delete_excessive_objects(swift_conn, threshold):
    """
    just for demo
    get the number of objects in container, if it's beyond threshold, then
    delete the whole container, and create a new one.
    """
    logging.debug('objects num before delete: not implemented')


# def subfunc():
#     print('threading %s running...' % threading.current_thread().name)
#     # datain = raw_input('pleas input: ')

#     print('threading %s ending...' % threading.current_thread().name)


class ThreadExcessiveReaper(threading.Thread):
    def __init__(self, thread_name, swift_conn, conf):
        threading.Thread.__init__(self, name=thread_name)
        self.swift_conn = swift_conn
        self.threshold = conf.threshold_container
        self.container = conf.container_video

    def run(self):
        while 1:
            try:
                head_container = self.swift_conn.head_container(
                    self.container)
                obj_counts = head_container['x-container-object-count']
                logging.debug('objects count: %s' % obj_counts)
            except:
                logging.debug('exception when head_container in \
                              ExcessiveReaper')
                break
            else:
                if obj_counts > self.threshold:
                    logging.debug('obj over threshold, try to delete')
                    try:
                        self.swift_conn.delete_container(self.container)
                    except:
                        logging.debug('container delete fail')
                    else:
                        logging.debug('container delete success')


class ThreadStoredReaper(threading.Thread):
    def __init__(self, thread_name, swift_conn, conf):
        threading.Thread.__init__(self, name=thread_name)
        self.swift_conn = swift_conn
        self.threshold = conf.threshold_container
        self.container = conf.container_video

    def run(self):
        pass


@funclogger('--------process---------')
def process(start_time, stop_time=None, duration=5):
    """
    cut the video based on the time parameters via ffmpeg,
    then upload the video to swift

    :start_time
    :stop_time
    :duration, if the stop_time is None, then cut the video for 5 seconds 
    by default
    """
    conf = Config()
    if not os.path.isdir(conf.video_dir):
        logging.info('video dir does not exists, start to create...')
        os.mkdir(conf.video_dir)
    if not os.path.isdir(conf.upload_dir):
        logging.info('upload dir does not exists, start to create...')
        os.mkdir(conf.upload_dir)
    if len(os.listdir(conf.video_dir)) < 1:
        logging.info('video dir has no video right now, wait %s...' % 
            conf.wait_for_video_sec)
        time.sleep(conf.wait_for_video_sec)
    video_editted = videoedit.editting(start_time, stop_time, 
                                                            conf.video_dir, conf.upload_dir)

    if conf.no_catch:
        pass
    else:
        pass
        # cut the video via ffmpeg by shell scripts
        # child_catch = subprocess.Popen('exec sh ' + conf.shell_dir, shell=True)
        # logging.debug('child_catch pid: %s starting...' % child_catch.pid)

    conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
    # check if container exists, create one if not
    try:
        head_container = conn.head_container(conf.container_video)
        logging.info('head container: %s' % json.dumps(head_container, 
            sort_keys=True, indent=4))
    except:
        logging.debug('container not exists or swift connection fail...')
        conn.put_container(conf.container_video)
        logging.debug('created container...')

    try:
        logging.info('start to upload...')
        # swift_upload(conn, conf)
        logging.debug('conn uploading video: %s' % video_editted)
        file = open(video_editted)
        conn.put_object(conf.container_video, video_editted[-25:], file)
        # swift_conn.put_object(CONTAINER, pathname, file)
        logging.debug('conn after uploading video: %s' % video_editted)
    except:
        logging.debug('upload object failed, something is wrong, i can feel \
            it...')
    else:
        logging.debug('finish uploading, to delete or rename the uploaded \
            video...')
        # if conf.auto_rename:
            # time.sleep(1)
            # rename(video)
        # else:
            # time.sleep(1)
            # delete_stored(video_editted)


class Processor(threading.Thread):
    def __init__(self, thread_name, queue):
        threading.Thread.__init__(self, name=thread_name)
        self.queue = queue

    def run(self):
        logging.info('start to run process...')
        while 1:
            logging.info('queue size: %s' % self.queue.qsize())
            item = self.queue.get()
            logging.info('queue item: %s' % item)
            start_time = item.get('vtime_start')
            end_time = item.get('vtime_end')
            if  start_time and end_time:
                logging.debug('start:%s, end:%s' % (start_time, end_time))
                time.sleep(2)
                logging.debug('after process, start:%s, end:%s' % 
                    (int(str(start_time)[:10]), int(str(end_time)[:10])))                
                process(int(str(start_time)[:10]), int(str(end_time)[:10]))
            else:
                logging.info('received start time or end time error!')
            self.queue.task_done()            


if __name__ == '__main__':
    #main()
    pass