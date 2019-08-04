from datetime import datetime

schema = [
    ('citizen_id', {
        'type': int,
        'primary': True,
        'order': 0
    }),
    ('town', {
        'type': str,
        'order': 1
    }),
    ('street', {
        'type': str,
        'order': 2
    }),
    ('building', {
        'type': str,
        'order': 3
    }),
    ('apartment', {
        'type': int,
        'order': 4
    }),
    ('name', {
        'type': str,
        'order': 5,
    }),
    ('gender', {
        'type': str,
        'values': ['male', 'female'],
        'order': 6
    }),
    ('relatives', {
        'type': list,
        'order': 7
    }),
    ('birth_date', {
        'type': str,
        'order': 8
    })
]

date_format = '%d.%m.%Y'


def date_validate(s):
    try:
        datetime.strptime(s, date_format)
    except:
        return False
    else:
        return True


def citizen_validate(citizen, update=False):

    for name, options in schema:
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

    output:
    result -> tuple(status -> boolean, message -> str)
    """

    # check json structure

    if not isinstance(data, list):
        return False, 'invalid data format'

    # check citizens field types and collect relative
    relatives = {}
    for citizen in data:
        if citizen_validate(citizen):
            relatives[citizen['citizen_id']] = citizen['relatives']
        else:
            i = citizen.get('citizen_id')
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
        for name, options in schema:
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
    new format -> [['=', index, new_value], ...]
    
    """
    result_data = []
    for name, value in data:
        pass


def format_from(data):
    result_data = {}
    result_data['citizens'] = []
    for citizen in data:
        dict_citizen = {}
        for name, options in schema:
            if name == 'birth_date':
                date_i = options['order']
                date = "{:02d}.{:02d}.{}".format(
                    citizen[date_i + 0],
                    citizen[date_i + 1],
                    citizen[date_i + 2])
                dict_citizen[name] = date
            else:
                dict_citizen[name] = citizen[options['order']]
        result_data['citizens'].append(dict_citizen)
    return result_data
