# -*- coding: utf8 -*-
from __future__ import absolute_import, division, print_function

import unittest
# import mock
import random
import logging

import swiftclient
from videoedit import videos_in_duration

logging.basicConfig(level=logging.DEBUG)

class CatchuploadTestCase(unittest.TestCase):
    def setUp(self):
        conf = Config('./test_settings.conf')
        logging.info('conf: %s' % conf)
        # reaper = ThreadExcessiveReaper('reapertest', conn, conf)
    def tearDown(self):
        pass

    def test_videos_in_duration(self):
      pass


if __name__ == '__main__':
    unittest.main()
