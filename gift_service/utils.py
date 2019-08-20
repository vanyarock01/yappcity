from datetime import datetime
import numpy as np

schema = {
    'citizen_id': {
        'type': int,
        'primary': True,
        'order': 0
    }, 'town': {
        'type': str,
        'order': 1
    }, 'street': {
        'type': str,
        'order': 2
    }, 'building': {
        'type': str,
        'order': 3
    }, 'apartment': {
        'type': int,
        'order': 4
    }, 'name': {
        'type': str,
        'order': 5,
    }, 'gender': {
        'type': str,
        'values': ['male', 'female'],
        'order': 6
    }, 'relatives': {
        'type': list,
        'order': 7
    }, 'birth_date': {
        'type': str,
        'order': 8
    }
}


def get_field(citizen, field_name):
    return citizen[schema[field_name]['order']]


def get_pos(field_name):
    return schema[field_name]['order']


date_format = '%d.%m.%Y'


def date_validate(s):
    try:
        datetime.strptime(s, date_format)
    except:
        return False
    else:
        return True


def citizen_validate(citizen, update=False):
    for name, options in schema.items():
        if citizen.get(name) is None:
            if not update:
                return False
        else:
            if update and options.get('primary') == True:
                return False
            elif name == 'relatives' and \
                    not all(isinstance(n, int) for n in citizen.get('relatives')):
                return False
            elif name == 'birth_date' and \
                    not date_validate(citizen.get('birth_date')):
                return False
            elif name == 'gender' and \
                    citizen.get('gender') not in options['values']:
                return False
            elif not isinstance(citizen.get(name), options['type']):
                return False
    return True


def validate(data):
    """ data validation
    input:
    data -> dict { 'citizens': [{}, ...] }

    return:
    result -> tuple(status -> boolean, message -> str)
    """

    # check json structure
    if not isinstance(data, list):
        return False, 'invalid data format'

    # check citizens field types and collect relative
    relatives = {}

    for citizen in data:
        i = citizen.get('citizen_id')
        if relatives.get(i) == None and citizen_validate(citizen):
            relatives[i] = citizen['relatives']
        else:
            return False, f'invalid citizen format id {str(i)}'
    # check relatives
    for i, rel in relatives.items():
        for r in rel:
            if i not in relatives[r]:
                return False, f'invalid relatives: citzen {i} not in relatives citzen {r}'
    return True, 'ok'


def format_to(data):
    """ format data from dict format to lists
        use only after succesfull run validate function
    """
    result_data = []
    tuple_len = len(schema) + 2  # birth_date -> birth_d, birth_m, birth_y

    for citizen in data['citizens']:
        note_citizen = [None] * tuple_len
        for name, options in schema.items():
            if name == 'birth_date':
                date = datetime.strptime(citizen['birth_date'], date_format)
                # index: [...,   8,     9,   10]
                # tuple: [..., day, month, year]
                note_citizen[options['order'] + 0] = date.day
                note_citizen[options['order'] + 1] = date.month
                note_citizen[options['order'] + 2] = date.year
            else:
                note_citizen[options['order']] = citizen[name]

        result_data.append(note_citizen)
    return result_data


def format_to_optional(data):
    """format data to update citizen info
    new format -> [('=', index, new_value), ...]
    """
    result_data = []
    for name, value in data.items():
        result_data.append(('=', schema[name]['order'], value))

    return result_data


def diff(a, b):
    b = set(b)
    return [e for e in a if e not in b]

# increment in <position> it needed due to the fact that in lua arrays are numbered from 1

def citizen_data_shaper(citizen_id, citizen_data):
    """addition of data for updating a citizen
    return:
    (citizen_id, [('=', <position>, <value>), (), (), ...])
    """

    positions_values = []
    data = (citizen_id, positions_values)

    for name, value in citizen_data.items():
        pos = get_pos(name)
        
        if name == 'birth_date':
            date = datetime.strptime(value, date_format)
            positions_values += [
                ('=', pos + 1, date.day),
                ('=', pos + 2, date.month),
                ('=', pos + 3, date.year)                
            ]
        else:
            positions_values.append(('=', pos + 1, value))

    return data


def relative_data_shaper(citizen_id, cur_relatives, new_relatives, relatives_pack):
    """addition of data for updating relatives between citizens
    return:
    [ 
        (citizen_id, [('=', <position>, <value>), (), (), ...]),
        ...
    ]
    """
    update_data = []

    # if relations change, you need to change them with relatives citizens
    # cur_relatives = cur_citizen[schema['relatives']['order']]

    remove = diff(cur_relatives, new_relatives)
    insert = diff(new_relatives, cur_relatives)

    for citizen in relatives_pack:
        i = get_field(citizen, 'citizen_id')
        if i in remove:
            get_field(citizen, 'relatives').remove(citizen_id)
            new_relatives = get_field(citizen, 'relatives')
        elif i in insert:
            get_field(citizen, 'relatives').append(citizen_id)
            new_relatives = get_field(citizen, 'relatives')
        else:
            continue
        update_data.append(
            (i, [('=', get_pos('relatives') + 1, new_relatives)]))

    return update_data


def format_citizen(raw):
    dict_citizen = {}
    for name, options in schema.items():
        if name == 'birth_date':
            date_i = options['order']
            date = "{:02d}.{:02d}.{}".format(
                raw[date_i + 0],
                raw[date_i + 1],
                raw[date_i + 2])
            dict_citizen[name] = date
        else:
            dict_citizen[name] = raw[options['order']]
    return dict_citizen

def percentiles(data, p):
    result = {}
    for val in p:
        result['p' + str(val)] = int(np.percentile(np.array(data), val))
    return result
