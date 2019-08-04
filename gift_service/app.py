import tarantool
import logging
import falcon
import utils
import json

connection = tarantool.connect(host='localhost', port=3331)
logging.basicConfig(filename='app.log', level=logging.DEBUG)


class SampleImport():
    def on_post(self, req, resp):
        posted_data = json.loads(req.stream.read())
        if not posted_data:
            resp.status = falcon.HTTP_400
            resp.body = "empty data"
            return

        valid, msg = utils.validate(posted_data)

        if not valid:
            resp.status = falcon.HTTP_400
            resp.body = msg
        else:
            formatted = utils.format_to(posted_data)
            ret = connection.call('sample_create', [formatted])

            resp.status = falcon.HTTP_201
            resp.body  = json.dumps({'import_id': ret.data[0]})


    def on_get(self, req, resp, import_id):
        ret = connection.call('sample_all', [import_id])
        formatted = utils.format_from(ret.data[0])
        # logging.debug(formatted)
        # logging.debug(type(formatted))
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(formatted)

    def on_patch(self, req, resp, import_id, citizen_id):
        posted_data = json.loads(req.stream.read())





api = falcon.API()

sample_import = SampleImport()

api.add_route('/imports', sample_import)
api.add_route('/imports/{import_id}', sample_import)
api.add_route('/imports/{import_id}/citizens/{citizen_id}', sample_import)