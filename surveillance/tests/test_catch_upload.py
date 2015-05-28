# -*- coding: utf8 -*-
from __future__ import absolute_import, division, print_function

import unittest
# import mock
import random
import logging

import swiftclient
from process import ThreadExcessiveReaper, Config

logging.basicConfig(level=logging.DEBUG)

class CatchuploadTestCase(unittest.TestCase):
    def setUp(self):
        conf = Config('./test_settings.conf')
        conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
        logging.info('conf: %s' % conf)
        # reaper = ThreadExcessiveReaper('reapertest', conn, conf)
    def tearDown(self):
        pass


# if __name__ == '__main__':
#     unittest.main()
