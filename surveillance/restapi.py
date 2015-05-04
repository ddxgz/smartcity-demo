import falcon
import json


class ThingsRe:
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
        except:
            raise falcon.HTTPError(falcon.HTTP_400, 'malformed json')
        resp.status = falcon.HTTP_202
        resp.body = json.dumps(result_json, encoding='utf-8')

app = falcon.API()

things = ThingsRe()

app.add_route('/things', things)
