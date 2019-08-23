import tarantool
import logging
import falcon
import utils
import mware
import json

connection = tarantool.connect(host='localhost', port=3331)
logging.basicConfig(filename='app.log', level=logging.DEBUG)


def tarantool_call(function_name, *args):
    # the connection.call puts the result in the "data" field
    # and in the list (why didn’t I find out so)
    data = connection.call(function_name, args).data[0]

    logging.debug(f"TARANTOOL call, function={function_name}")
    logging.debug('args')
    logging.debug(args)
    logging.debug('data')
    logging.debug(data)

    if data is None:
        raise falcon.HTTPBadRequest('Import not found.')



    return data


class Import():
    def on_post(self, req, resp):
        posted_data = req.context['request']
        valid, msg = utils.validate(posted_data)

        if not valid:
            resp.status = falcon.HTTP_400
            return

        formatted = utils.format_to(posted_data)
        ret = tarantool_call('import_create', formatted)


        resp.status = falcon.HTTP_201
        resp.context['response'] = {
            'import_id': ret
        }

    def on_get(self, req, resp, import_id):
        raw_citizens = tarantool_call('import_all', import_id)

        form_citizens = []
        for citizen in raw_citizens:
            form_citizens.append(utils.format_citizen(citizen))

        resp.status = falcon.HTTP_200
        resp.context['response'] = form_citizens


    def on_patch(self, req, resp, import_id, citizen_id):
        posted_data = req.context['request']

        valid = utils.citizen_validate(posted_data, update=True)

        if not valid:
            resp.status = falcon.HTTP_400
            return

        data = []
        citizen_data = utils.citizen_data_shaper(citizen_id, posted_data)
        data.append(citizen_data)

        if posted_data.get('relatives'):
            citizen_pack = tarantool_call(
                'import_citizen_with_relative',
                import_id,
                citizen_id,
                posted_data['relatives'])

            relative_data = utils.relative_data_shaper(
                citizen_id=citizen_id,
                cur_relatives=utils.get_field(
                    citizen_pack[0], 'relatives'),
                new_relatives=posted_data['relatives'],
                relatives_pack=citizen_pack[1])
        else:
            relative_data = []

        data += relative_data
        updated_citizen = tarantool_call(
            'import_update_citizens',
            import_id,
            data)

        
        resp.status = falcon.HTTP_200
        resp.context['response'] = utils.format_citizen(updated_citizen)


class ImportBirthdays():
    def on_get(self, req, resp, import_id):
        #TODO: if import dont exist - 400: bad request
        raw_birtdays = tarantool_call('import_birthdays', import_id)

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
        resp.context['response'] = new_birtdays


class ImportTownsAges():
    def on_get(self, req, resp, import_id):
        #TODO: if import dont exist - 400: bad request
        towns_stat = tarantool_call('import_towns_ages', import_id)

        towns_percentiles = []

        for town, ages in towns_stat.items():
            stat = utils.percentiles(ages, [50, 75, 99])
            stat['town'] = town
            towns_percentiles.append(stat)

        resp.status = falcon.HTTP_200
        resp.context['response'] = towns_percentiles


api = falcon.API(middleware=[
    mware.JSONprocess(),
])

import_class = Import()

api.add_route('/imports', import_class)
api.add_route('/imports/{import_id:int(min=0)}/citizens', import_class)
api.add_route('/imports/{import_id:int(min=0)}/citizens/{citizen_id:int(min=0)}', import_class)

birtdays_class = ImportBirthdays()
api.add_route('/imports/{import_id:int(min=0)}/citizens/birthdays', birtdays_class)

towns_ages_class = ImportTownsAges()
api.add_route('/imports/{import_id:int(min=0)}/towns/stat/percentile/age', towns_ages_class)
