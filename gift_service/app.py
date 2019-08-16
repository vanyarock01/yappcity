import tarantool
import logging
import falcon
import utils
import json

connection = tarantool.connect(host='localhost', port=3331)
logging.basicConfig(filename='app.log', level=logging.DEBUG)


def tarantool_call(function_name, *args):
    try:
        # the connection.call puts the result in the "data" field
        # and in the list (why didn’t I find out so)
        data = connection.call(function_name, args).data[0]
        status = True
    except Exception as e:
        status, data = False, str(e)

    logging.debug(f"TARANTOOL call, function={function_name}, status={status}")
    logging.debug('args')
    logging.debug(args)
    logging.debug('data')
    logging.debug(data)

    return status, data


class SampleImport():
    def on_post(self, req, resp):
        posted_data = json.loads(req.stream.read())

        # check json structure
        if not posted_data or not isinstance(posted_data, dict) or \
                posted_data.get('citizens') is None:

            resp.status = falcon.HTTP_400
            resp.body = "empty data"
            return

        valid, msg = utils.validate(posted_data['citizens'])

        if not valid:
            resp.status = falcon.HTTP_400
            resp.body = msg
        else:
            formatted = utils.format_to(posted_data)
            status, ret = tarantool_call('sample_create', formatted)

            resp.status = falcon.HTTP_201
            resp.body = json.dumps({'import_id': ret})

    def on_get(self, req, resp, import_id):
        status, raw_citizens = tarantool_call('sample_all', import_id)
        
        form_citizens = []
        for citizen in raw_citizens:
            form_citizens.append(utils.format_citizen(citizen))

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({'citizens': form_citizens})

    def on_patch(self, req, resp, import_id, citizen_id):
        citizen_id = int(citizen_id)

        posted_data = json.loads(req.stream.read())

        if not posted_data:
            resp.status = falcon.HTTP_400
            resp.body = "empty data"
            return

        valid = utils.citizen_validate(posted_data, update=True)

        if not valid:
            resp.status = falcon.HTTP_400
        else:
            data = []
            citizen_data = utils.citizen_data_shaper(citizen_id, posted_data)
            data.append(citizen_data)

            if posted_data.get('relatives'):
                status, citizen_pack = tarantool_call(
                    'sample_citizen_with_relative',
                    import_id,
                    citizen_id,
                    posted_data['relatives'])

                relative_data = utils.relative_data_shaper(
                    citizen_id=citizen_id,
                    cur_relatives=utils.get_field(citizen_pack[0], 'relatives'),
                    new_relatives=posted_data['relatives'],
                    relatives_pack=citizen_pack[1])
            else:
                relative_data = []

            data += relative_data
            status, updated_citizen = tarantool_call(
                'sample_update_citizens',
                import_id,
                data)

            resp.body = json.dumps(utils.format_citizen(updated_citizen))
            resp.status = falcon.HTTP_201


class SampleBirthdays():
    def on_get(self, req, resp, import_id):
        status, raw_birtdays = tarantool_call('sample_birthdays', import_id)

        # format data
        new_birtdays = {}
        for month, raw_data in raw_birtdays.items():
            new_data = []
            if len(raw_data) > 0:
                for citizen_id, presents in raw_data.items():
                    new_data.append({
                        'citizen_id': citizen_id,
                        'presents': presents
                    })
            new_birtdays[month] = new_data

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({'data': new_birtdays})

api = falcon.API()

sample_import = SampleImport()

api.add_route('/imports', sample_import)
api.add_route('/imports/{import_id}', sample_import)
api.add_route('/imports/{import_id}/citizens/{citizen_id}', sample_import)

sample_birtdays = SampleBirthdays()
api.add_route('/imports/{import_id}/citizens/birthdays', sample_birtdays)
