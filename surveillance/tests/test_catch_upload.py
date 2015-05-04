# -*- coding: utf8 -*-

import unittest
import mock
import random

import swiftclient
from surveillance import ThreadExcessiveReaper, Config

class CatchuploadTestCase(unittest.TestCase):
    def setUp(self):
        conf = Config()
        conn = swiftclient.Connection(conf.auth_url,
                                  conf.account_username,
                                  conf.password,
                                  auth_version=conf.auth_version)
        reaper = ThreadExcessiveReaper('reapertest', conn, conf)
    def tearDown(self):
        pass
