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
from config import Config
from utils import funclogger, time2Stamp, stamp2Time

# logging.basicConfig(filename='log_process.log', filemode='w', level=logging.DEBUG)
# logging.basicConfig(format='===========My:%(levelname)s:%(message)s=========', 
#     level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG,
#                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                 datefmt='%d %b %Y %H:%M:%S')


@funclogger('--------auto_rename---------')
def rename(pathname):
    newname = pathname[:len(pathname)-14] + str(time.time())[0:10] + pathname[-4:]
    logging.info('rename to newname: %s' % newname)
    os.rename(pathname, newname)


@funclogger('-------swift_upload-------')
def swift_upload(swift_conn, conf):
    videos = videos2upload(conf)
    logging.info('videos: %s ' % videos)
    if not videos or len(videos) is 0:
        logging.info('no video can be uploaded, wait: %s seconds' % 
            conf.uploading_interval)
        time.sleep(conf.uploading_interval)
        videos = videos2upload(conf)
    logging.info('videos after sleep: %s ' % videos)
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


class ThreadExcessiveReaper(threading.Thread):
    """
    not used
    """
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
    """
    not used
    """
    def __init__(self, thread_name, swift_conn, conf):
        threading.Thread.__init__(self, name=thread_name)
        self.swift_conn = swift_conn
        self.threshold = conf.threshold_container
        self.container = conf.container_video

    def run(self):
        pass


@funclogger('--------process---------')
def process(start_time, stop_time=None, event_name='', duration=5):
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
        
    try:
        logging.debug('start to get the video file...')
        video_editted = videoedit.editting(start_time, stop_time, 
                                        conf.video_dir, conf.upload_dir)
    except:
        logging.debug('exception when get the video file \
            by videoedit.editting()')

    if conf.no_catch:
        pass
    else:
        pass

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
        videofile = open(video_editted)
        conn.put_object(container=conf.container_video, 
            obj=event_name+video_editted[-25:], contents=videofile)
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


def get_event(state_in):
    """
    return the event name by the state of coming message
    """
    if state_in is not None:
        if state_in == 0:
            return 'leaving_'
        else:
            return 'person_' + str(state_in) + '_in_'


class Processor(threading.Thread):
    """
    Receive the messages via a queue from REST API requests, parse the param
    in the message and pass params to process 
    """
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
            event_name = get_event(item.get('state'))
            if start_time and end_time:
                logging.debug('start:{}, end:{}'.format(start_time, end_time))
                # wait a few seconds to let the video to be catched
                time.sleep(5)
                logging.debug('after process, start:%s, end:%s' % 
                    (int(str(start_time-1)[:10]), int(str(end_time+1)[:10])))                
                process(int(str(start_time)[:10]), int(str(end_time)[:10]), 
                    event_name=event_name)
            else:
                logging.info('error of received start time or end time!')
            self.queue.task_done()            


# if __name__ == '__main__':
#     #main()
#     pass