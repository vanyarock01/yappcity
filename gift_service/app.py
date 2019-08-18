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

        if not posted_data or not isinstance(posted_data, dict) or \
                posted_data.get('citizens') is None:
            resp.status = falcon.HTTP_400
            return
        valid, msg = utils.validate(posted_data['citizens'])

        if not valid:
            resp.status = falcon.HTTP_400
            return

        formatted = utils.format_to(posted_data)
        status, ret = tarantool_call('sample_create', formatted)

        if not status:
            resp.status = falcon.HTTP_500
            resp.body = ret
            return

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({
            'data': {
                'import_id': ret
            }
        })

    def on_get(self, req, resp, import_id):
        #TODO: if import dont exist - 400: bad request
        status, raw_citizens = tarantool_call('sample_all', import_id)
        if not status:
            resp.status = falcon.HTTP_500
            resp.body = raw_citizens
            return

        form_citizens = []
        for citizen in raw_citizens:
            form_citizens.append(utils.format_citizen(citizen))

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'data': form_citizens
        })

    def on_patch(self, req, resp, import_id, citizen_id):
        try:
            citizen_id = int(citizen_id)
            posted_data = json.loads(req.stream.read())
            valid = utils.citizen_validate(posted_data, update=True)
        except:
            resp.status = falcon.HTTP_400
            return

        if not valid:
            resp.status = falcon.HTTP_400
            return

        data = []
        citizen_data = utils.citizen_data_shaper(citizen_id, posted_data)
        data.append(citizen_data)

        if posted_data.get('relatives'):
            status, citizen_pack = tarantool_call(
                'sample_citizen_with_relative',
                import_id,
                citizen_id,
                posted_data['relatives'])

            if not status:
                resp.status = falcon.HTTP_500
                resp.body = citizen_pack
                return

            relative_data = utils.relative_data_shaper(
                citizen_id=citizen_id,
                cur_relatives=utils.get_field(
                    citizen_pack[0], 'relatives'),
                new_relatives=posted_data['relatives'],
                relatives_pack=citizen_pack[1])
        else:
            relative_data = []

        data += relative_data
        status, updated_citizen = tarantool_call(
            'sample_update_citizens',
            import_id,
            data)

        if not status:
            resp.status = falcon.HTTP_500
            resp.body = updated_citizen
            return

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'data': utils.format_citizen(updated_citizen)
        })


class SampleBirthdays():
    def on_get(self, req, resp, import_id):
        #TODO: if import dont exist - 400: bad request
        status, raw_birtdays = tarantool_call('sample_birthdays', import_id)

        if not status:
            resp.status = falcon.HTTP_500
            resp.body = raw_birtdays
            return

        # format data
        new_birtdays = {}
        for month, raw_data in raw_birtdays.items():
            new_data = []
            # unpleasant feature of converting Lua tables into Python structures
            # if the table is empty it is converted to an empty list and not a dict
            if len(raw_data) > 0:
                for citizen_id, presents in raw_data.items():
                    new_data.append({
                        'citizen_id': citizen_id,
                        'presents': presents
                    })
            new_birtdays[month] = new_data

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'data': new_birtdays
        })


class SampleTownsAges():
    def on_get(self, req, resp, import_id):
        #TODO: if import dont exist - 400: bad request
        status, towns_stat = tarantool_call('sample_towns_ages', import_id)

        if not status:
            resp.status = falcon.HTTP_500
            resp.body = raw_birtdays
            return

        towns_percentiles = []

        for town, ages in towns_stat.items():
            stat = utils.percentiles(ages, [50, 75, 99])
            stat['town'] = town
            towns_percentiles.append(stat)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'data': towns_percentiles
        })


api = falcon.API()

sample_import = SampleImport()

api.add_route('/imports', sample_import)
api.add_route('/imports/{import_id}/citizens', sample_import)
api.add_route('/imports/{import_id}/citizens/{citizen_id}', sample_import)

sample_birtdays = SampleBirthdays()
api.add_route('/imports/{import_id}/citizens/birthdays', sample_birtdays)

sample_towns_ages = SampleTownsAges()
api.add_route('/imports/{import_id}/towns/stat/percentile/age', sample_towns_ages)
