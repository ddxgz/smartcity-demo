# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os, sys, subprocess, time
import signal
import logging

from six.moves import configparser

from config import Config
from utils import funclogger, time2Stamp, stamp2Time

# logging.basicConfig(filename='log_process.log', filemode='w', level=logging.DEBUG)
# logging.basicConfig(format='===========My:%(levelname)s:%(message)s=========', 
#     level=logging.DEBUG)
logging.basicConfig(filename='log_start.log', filemode='w',
                level=logging.DEBUG,
                format='[%(levelname)s] %(message)s [%(filename)s][line:%(lineno)d] %(asctime)s ',
                datefmt='%d %b %Y %H:%M:%S')


def signal_exit_handler(signal, frame):
    print('You pressed Ctrl+C, start to stop all the processes...')
    for pid in PIDS:
        os.killpg(pid, signal.SIGTERM)
        logging.debug('killed pid: %s ...' % pid)
    sys.exit(0)


def startall():
    # child_catch = subprocess.Popen('sh ' + SHELL_DIR, shell=True,
    #     preexec_fn=os.setsid)
    conf = Config()
    pids = []
    child_catch = subprocess.Popen('exec nohup sh ' + conf.shell_dir, 
        shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    pids.append(child_catch.pid)
    logging.debug('child_catch pid: %s starting...' % child_catch.pid)
    
    child_gunicorn = subprocess.Popen(['gunicorn', '-b', '0.0.0.0:8008', 
        'restapi:app'], stdout=subprocess.PIPE, preexec_fn=os.setsid)
    pids.append(child_gunicorn.pid)
    logging.debug('child_gunicorn pid: %s starting...' % child_gunicorn.pid)
    
    child_reaper = subprocess.Popen(['python', './reaper.py'], 
        stdout=subprocess.PIPE, preexec_fn=os.setsid)
    pids.append(child_reaper.pid)
    logging.debug('child_reaper pid: %s starting...' % child_reaper.pid)

    # child_swiftbrowser = subprocess.Popen(['python', 
    #     '/root/swift-webstorage/manage.py', 'runserver', '0.0.0.0:8000'], 
    #     stdout=subprocess.PIPE, preexec_fn=os.setsid)
    # pids.append(child_swiftbrowser.pid)
    # logging.debug('child_swiftbrowser pid: %s starting...' % child_swiftbrowser.pid)

    # child_sensordbclient = subprocess.Popen(['java', '-jar', 
    #     '/root/sensordb-client/sensordb-client.jar'], 
    #     stdout=subprocess.PIPE, preexec_fn=os.setsid)
    # pids.append(child_sensordbclient.pid)
    # logging.debug('child_sensordbclient pid: %s starting...' % child_sensordbclient.pid)

    pidfile = open('./pids', 'w')
    for pid in pids:
        pidfile.write(str(pid) + '\n')
    # child_gunicorn = subprocess.Popen('exec gunicorn -b 0.0.0.0:8008 restapi:app')
    # logging.debug('child_gunicorn pid: %s starting...' % child_gunicorn.pid)

    # open a new thread to delete, only in dev
    # delete_excessive_objects(conn, conf.threshold_container)

    # open a new thread
    # delete_stored(conn)

    # child_catch.terminate()
    ## cannot use popenobj.kill() to kill child, it will just kill the shell
    ## need to put exec in Popen before cmd
    # child_catch.kill()
    # child_catch.wait()



if __name__ == '__main__':
    # signal.signal(signal.SIGINT, signal_exit_handler)
    # signal.pause()
    startall()
    # pass