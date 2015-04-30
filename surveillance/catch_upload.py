# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import commands
import os, signal, subprocess, time
import glob
import logging

from six.moves import configparser

import swiftclient

# didn't used
import threading


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
    def __init__(self):
        self._get_config()

    def _get_config(self):
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
            self.local_dir = config.get('catchconf', 'local_dir')
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


def swift_upload(swift_conn, conf):
    videos = videos2upload(conf)
    for video in videos:
        # upload(video)
        # swift_upload(swift_conn, video)
        logging.debug('swift_conn uploading video: %s' % video)
        file = open(video)
        swift_conn.put_object(conf.container_video, video[-19:], file)
        # swift_conn.put_object(CONTAINER, pathname, file)
        logging.debug('swift_conn after uploading video: %s' % video)
        delete_uploaded(video)


# def swift_upload(swift_conn, pathname):
#     logging.debug('swift_conn uploading video: %s' % pathname)
#     file = open(pathname)
#     swift_conn.put_object(CONTAINER, pathname[-19:], file)
#     # swift_conn.put_object(CONTAINER, pathname, file)
#     logging.debug('swift_conn after uploading video: %s' % pathname)


def delete_uploaded(pathname):
    # stat = commands.getoutput("rm " + LOCAL_DIR + "*." + suffix)
    # instead of os.remove()
    stat = commands.getoutput("rm " + pathname)
    logging.debug('deleted video: %s' % pathname)
    print(stat)


def videos2upload(conf):
    """
    get all the videos in the path, remove the latest one from list
    """
    logging.debug('dir: %s' % conf.local_dir + conf.upload_file)
    video_list = glob.glob(conf.local_dir + conf.upload_file)
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


def main():
    conf = Config()
    conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
    account_head = conn.head_account()
    # check if container exists, create one if not
    conn.put_container(conf.container_video)
    logging.debug('created container...')
    # child_catch = subprocess.Popen('sh ' + SHELL_DIR, shell=True,
    #     preexec_fn=os.setsid)
    child_catch = subprocess.Popen('exec sh ' + conf.shell_dir, shell=True)
    logging.debug('child_catch pid: %s starting...' % child_catch.pid)

    # open a new thread to delete, only in dev
    delete_excessive_objects(conn, conf.threshold_container)

    # open a new thread
    delete_stored(conn)

    cnt = 1
    while 1:
        print('start to upload...')
        swift_upload(conn, conf)
        time.sleep(conf.uploading_interval)
        logging.debug('########## cnt: %d ' % cnt)
        cnt += 1
        if cnt > conf.loopcount:
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
    logging.debug('child_catch killed...')

    # upload(LOCAL_DIR, UPLOAD_FILE)
    # delete_uploaded('mp4')


if __name__ == '__main__':
    main()
