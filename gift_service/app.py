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

        valid, msg = utils.validate(posted_data)

        logging.debug(valid)
        
        if not valid:
            resp.status = falcon.HTTP_400
        else:
            formatted = utils.format_to(posted_data)
            logging.debug(formatted)
            ret = connection.call('sample_create', [formatted])
            # logging.debug(ret)
            resp.status = falcon.HTTP_201
            resp.body  = str(ret.data[0])


    def on_get(self, req, resp, sample_id):
        ret = connection.call('sample_all', [sample_id])
        formatted = utils.format_from(ret.data[0])
        logging.debug(formatted)
        logging.debug(type(formatted))
        resp.status = falcon.HTTP_201
        resp.body = json.dumps(formatted)



api = falcon.API()

sample_import = SampleImport()

api.add_route('/imports', sample_import)
api.add_route('/imports/{sample_id}', sample_import)
