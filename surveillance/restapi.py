from __future__ import absolute_import, division, print_function
import falcon
import json
import Queue
import sys
import logging

from process import Processor

#sys.path.append('.')

class ThingsRe:
    def __init__(self):
        self.queue = Queue.Queue()
        self.processor = Processor('catch_upload processor', self.queue)
        self.processor.start()

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('\nTwo things awe me most, the starry sky '
                     'above me and the moral law within me.\n'
                     '\n'
                     '    ~ Immanuel Kant\n\n')

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
            print('req:%s' % raw_json)
        except:
            raise falcon.HTTPBadRequest('bad req')
        try:
            result_json = json.loads(raw_json, encoding='utf-8')
            print('result json:%s' % result_json)
            print('start to run process....')
            self.queue.put(result_json)
        except:
            raise falcon.HTTPError(falcon.HTTP_400, 'malformed json')
        resp.status = falcon.HTTP_202
        resp.body = json.dumps(result_json, encoding='utf-8')


class EventListener:
    def __init__(self):
        self.queue = Queue.Queue()
        self.processor = Processor('catch_upload processor', self.queue)
        self.processor.start()

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('\nTwo things awe me most, the starry sky '
                     'above me and the moral law within me.\n'
                     '\n'
                     '    ~ Immanuel Kant\n\n')

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
            logging.debug('req:%s' % raw_json)
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        try:
            result_json = json.loads(raw_json, encoding='utf-8')
            logging.debug('result json:%s' % result_json)
            logging.info('start to run process....')
            self.queue.put(result_json)
        except:
            raise falcon.HTTPError(falcon.HTTP_400, 'malformed json')
        resp.status = falcon.HTTP_202
        resp.body = json.dumps(result_json, encoding='utf-8')

app = falcon.API()

# things = ThingsRe()
event_listener = EventListener()

# app.add_route('/things', things)
app.add_route('/event', event_listener)
