import os
import commands
import time
import string
import logging
import functools

import swiftclient
from swiftclient.exceptions import ClientException

from utils import funclogger, time2Stamp, stamp2Time
from config import Config
from videoedit import get_file_with_prefix


# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG,
#                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                 datefmt='%d %b %Y %H:%M:%S')
logging.basicConfig(filename='log_reaper.log', filemode='w',
                level=logging.DEBUG,
                format='[%(levelname)s] %(message)s [%(filename)s][line:%(lineno)d] %(asctime)s ',
                datefmt='%d %b %Y %H:%M:%S')


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
            try:
                os.remove(conf.video_dir+old_video)
                logging.debug('removed: %s' % conf.video_dir+old_video)
            except:
                logging.error('failed to remove old video file:{}!'.format(
                    conf.video_dir+old_video))

    # uploaded_files =  os.listdir(conf.video_dir+'upload/')
    # for old_video in uploaded_files:
    #     os.remove(conf.video_dir+'upload/'+old_video)
    #     logging.debug('removed upload: %s' 
    #         % conf.video_dir+'upload/'+old_video)
    try:
        remove_all(conf.video_dir+'upload/')
        remove_all(conf.video_dir+'concats/')
    except:
        logging.error('failed to remove upload/ or concats/')



def container_reaper(num_threshold):
    conf = Config()
    conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
    try:
        container_head = conn.head_container(conf.container_video)
    except:
        logging.error('failed to head container!')
    logging.debug(container_head)
    if int(container_head['x-container-object-count']) > num_threshold:
        logging.debug('objects num: %s, delete container...' % 
            container_head['x-container-object-count'])
        time.sleep(5)
        try:
            conn.delete_container(conf.container_video)
        except ClientException:
            logging.error('failed to delete container!')
        time.sleep(5)
        try:
            conn.put_container(conf.container_video)
        except ClientException:
            logging.error('failed to put container!')


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

    # container_reaper(10)

    while 1:
        time.sleep(60*60)
        logging.debug('reaping videos....')
        videos_reaper(100)
        container_reaper(40)
