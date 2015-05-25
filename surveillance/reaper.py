import os
import commands
import time
import string
import logging
import functools

import swiftclient

from utils import funclogger, time2Stamp, stamp2Time
from process import Config
from videoedit import get_file_with_prefix

logging.basicConfig(level=logging.DEBUG)


def remove_all(path2file):
    files =  os.listdir(path2file)
    for afile in files:
        os.remove(path2file+afile)
        logging.debug('removed: %s' % path2file+afile)

@funclogger('------------editting----------')
def videos_reaper(num_threshold):
    conf = Config()
    logging.debug('folder:%s' % (conf.video_dir))
    files = os.listdir(conf.video_dir)
    logging.debug('files in source folder:%s' % files)
    videos = get_file_with_prefix(files, frefix='DEMO_')
    if len(videos) > num_threshold:
        videos.sort()
        logging.debug('videos:%s' % videos)
        old_videos = videos[0:len(videos)-num_threshold]
        for old_video in old_videos:
            os.remove(conf.video_dir+old_video)
            logging.debug('removed: %s' % conf.video_dir+old_video)
    # uploaded_files =  os.listdir(conf.video_dir+'upload/')
    # for old_video in uploaded_files:
    #     os.remove(conf.video_dir+'upload/'+old_video)
    #     logging.debug('removed upload: %s' 
    #         % conf.video_dir+'upload/'+old_video)
    remove_all(conf.video_dir+'upload/')
    remove_all(conf.video_dir+'concats/')


def container_reaper(num_threshold):
    conf = Config()
    conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
    container_head = conn.head_container(conf.container_video)
    logging.debug(container_head)
    if int(container_head['x-container-object-count']) > num_threshold:
        logging.debug('objects num: %s, delete container...' % 
            container_head['x-container-object-count'])
        time.sleep(5)
        conn.delete_container(conf.container_video)
        time.sleep(5)
        conn.put_container(conf.container_video)

# videos_reaper(3)
if __name__ == '__main__':
    # conf = Config()
    # conn = swiftclient.Connection(conf.auth_url,
    #                               conf.account_username,
    #                               conf.password,
    #                               auth_version=conf.auth_version)
    # conn.put_container(test_con)
    # # conn.delete_container(test_con)
    # # conn.delete_container(conf.container_video)
    # file1 = open('catch.sh')
    # conn.put_object(test_con, 'file1', file1)
    # conn.head_account()

    container_reaper(10)
    # while 1:
    #     time.sleep(60*60)
    #     logging.debug('reaping videos....')
    #     videos_reaper(100)
    #     container_reaper(40)
