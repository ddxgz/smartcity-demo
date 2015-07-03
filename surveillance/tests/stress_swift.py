# -*- coding: utf8 -*-
from __future__ import division, print_function

import time
# import mock
import random
import logging
import functools
import threading

import swiftclient
from config import  Config

logging.basicConfig(level=logging.INFO)


def generate_list(prefix, num):
    return [ prefix+str(i) for i in range(num) ]


def generate_obj_list(content, num):
    return [str.encode(content + str(i)) * 1000 for i in range(num) ]


def funclogger(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info('%s start func[%s]' % (text, func.__name__))
            start = time.time()
            result = func(*args, **kwargs)
            interval = time.time() - start
            logging.info('%s end func[%s], running: %0.5f seconds' % (text,
                func.__name__, interval))
            return result
        return wrapper
    return decorator


class SwiftStressTestCase:
    def __init__(self, con_num=1, obj_num=1, tag=''):
        self.tag = tag
        self.test_container = 'test_con_' + tag
        self.con_num = con_num
        self.obj_num = obj_num
        conf = Config('./test_settings.conf')
        self.conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)

    def test_create_container(self):
        for container in generate_list(self.test_container, self.con_num):
            self.conn.put_container(container)

    def test_head_container(self):
        for container in generate_list(self.test_container, self.con_num):
            container_head = self.conn.head_container(container)
            logging.debug('head container: %s' % container_head)

    def test_put_obj(self):
        for container in generate_list(self.test_container, self.con_num):
            for obj in generate_obj_list('content'+self.tag, self.obj_num):
                self.conn.put_object(container, obj[:10], obj)
            # logging.debug('head container: %s' % container_head)
    
    def tearDown(self):
        for container in generate_list(self.test_container, self.con_num):
            _m, objects = self.conn.get_container(container)
            for obj in objects:
                self.conn.delete_object(container, obj['name'])
            self.conn.delete_container(container)
        self.conn.close()

    def tearDown_man(self):
        for container in generate_list(self.test_container, self.con_num):
            # print(container[-2:])
            if len(container) == 11 and int(container[-2:]) >= 39:
                _m, objects = self.conn.get_container(container)
                for obj in objects:
                    self.conn.delete_object(container, obj['name'])
                self.conn.delete_container(container)
        self.conn.close()


class ThreadStressTest(threading.Thread):
    def __init__(self, thread_name):
        threading.Thread.__init__(self, name=thread_name)
        self.stresstest = SwiftStressTestCase(con_num=5, obj_num=10, 
            tag=thread_name)
        self.thread_name = thread_name

    def run(self):
        logging.info('-----------------------------------------\
            %s test_create_container start' % (self.thread_name))
        start = time.time()
        self.stresstest.test_create_container()
        interval = time.time() - start
        logging.info('------------------------------------------\
            %s test_create_container end, running: %0.5f seconds' % (
            self.thread_name, interval))
        # self.stresstest.test_head_container()
        logging.info('-------------------------------------------\
            %s test_put_obj start' % (self.thread_name))
        start = time.time()
        # self.stresstest.test_put_obj()
        interval = time.time() - start
        logging.info('-------------------------------------------\
            %s test_put_obj end, running: %0.5f seconds' % (
            self.thread_name, interval))
        self.stresstest.tearDown()

for i in range(3):
    thread = ThreadStressTest('t'+str(i))
    thread.start()

# stresstest = SwiftStressTestCase(con_num=1, obj_num=1)
# stresstest.test_create_container()
# stresstest.test_head_container()
# stresstest.test_put_obj()
# stresstest.tearDown_man()

# lit = generate_obj_list('abc', 5)
# print(lit[0][:2])
