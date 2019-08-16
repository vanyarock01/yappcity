#!/usr/bin/env python3
import collections
import requests
import sample
import helper
import json
import time


def validation_test_pack():
    print('BEGIN validation tests')
    test_pack = []

    test_pack.append((
        requests.post,
        'empty',
        400,
        {}))

    test_pack.append((
        requests.post,
        'empty citzens list',
        400,
        {'citzens': []}
    ))

    test_pack.append((
        requests.post,
        'missing field town',
        400,
        {'citizens': [
            {'citizen_id': 1, 'street': 'n', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [], 'birth_date': '21.04.1960'}
        ]}
    ))

    test_pack.append((
        requests.post,
        'invalid field citizen_id type',
        400,
        {'citizens': [
            {'citizen_id': '1', 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [], 'birth_date': '21.04.1960'}
        ]}
    ))

    test_pack.append((
        requests.post,
        'valid',
        201,
        {'citizens': [
            {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [2, 3], 'birth_date': '20.04.1960'},
            {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
            {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
        ]}
    ))

    test_pack.append((
        requests.post,
        'invalid relatives',
        400,
        {'citizens': [
            {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [3], 'birth_date': '20.04.1960'},
            {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
            {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
        ]}
    ))

    test_pack.append((
        requests.post,
        'invalid relatives types',
        400,
        {'citizens': [
            {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [2, 3], 'birth_date': '20.04.1960'},
            {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': ['1'], 'birth_date': '21.04.1960'},
            {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
             'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
        ]}
    ))

    for method, msg, code, data in test_pack:
        resp_test = method(
            'http://localhost:8000/imports', data=json.dumps(data))
        result = 'OK '
        if resp_test.status_code != code:
            result = 'ERR'
        print(f'{result} {resp_test.status_code} {msg} ')


def patch_test():
    print('BEGIN patch tests')

    resp_post = requests.post(
        'http://localhost:8000/imports',
        data=json.dumps(
            {'citizens': [
                {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [2, 3, 4], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1, 4], 'birth_date': '21.04.1960'},
                {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'},
                {'citizen_id': 4, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1, 2], 'birth_date': '22.04.1960'}
            ]}
        ))

    if resp_post.status_code != 201:
        print(f'ERR {resp_post.status_code} {resp_post.text}')
        return

    import_id = json.loads(resp_post.text)['import_id']
    print(f'IMPORT_ID {import_id}')

    test_pack = []
    test_pack.append((
        requests.patch,
        'optional validation',
        201,
        1,
        {'town': 'leon', 'building': 'new', 'apartment': 2,
         'name': 'koko', 'birth_date': '21.05.1970'},
        {'citizen_id': 1, 'street': 'n', 'town': 'leon', 'building': 'new', 'apartment': 2,
         'name': 'koko', 'gender': 'female', 'relatives': [2, 3, 4], 'birth_date': '21.05.1970'}
    ))

    test_pack.append((
        requests.patch,
        'optional validation with try update citzen_id',
        400,
        2,
        {'citizen_id': 1, 'town': 'm', 'building': 'n', 'apartment': 1,
         'name': 'k', 'birth_date': '20.04.1960'},
        None
    ))

    test_pack.append((
        requests.patch,
        'relative changing - insert',
        201,
        3,
        {'relatives': [1, 2]},
        {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1, 2], 'birth_date': '22.04.1960'}
    ))

    test_pack.append((
        requests.patch,
        'relative changing - remove',
        201,
        4,
        {'relatives': [1]},
        {'citizen_id': 4, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
    ))

    for method, msg, code, i, data, excepted in test_pack:
        resp_test = method(
            f'http://localhost:8000/imports/{import_id}/citizens/{i}', data=json.dumps(data))
        result = 'OK '
        if resp_test.status_code != code:
            result = 'ERR_CODE'
        
        if excepted and not helper.citizen_equivalent(excepted, json.loads(resp_test.text)):
            result = 'ERR_VAL'

        print(f'{result} {resp_test.status_code} {msg}')


def birtdays_test():
    print('BEGIN birthdays tests')
    resp_post = requests.post(
        'http://localhost:8000/imports',
        data=json.dumps(
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [], 'birth_date': '20.01.1960'},
                {'citizen_id': 2, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '21.02.1960'},
                {'citizen_id': 3, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [2, 6], 'birth_date': '22.03.1960'},
                {'citizen_id': 4, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [5], 'birth_date': '22.04.1960'},
                {'citizen_id': 5, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [4, 11, 9], 'birth_date': '22.05.1960'},
                {'citizen_id': 6, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '22.06.1960'},
                {'citizen_id': 7, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [], 'birth_date': '22.04.1960'},
                {'citizen_id': 8, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [9], 'birth_date': '22.03.1960'},
                {'citizen_id': 9, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [5, 8, 10], 'birth_date': '22.03.1960'},
                {'citizen_id': 10, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [9, 11], 'birth_date': '22.08.1960'},
                {'citizen_id': 11, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [5, 10], 'birth_date': '22.03.1960'}
            ]}
        ))

    excepted = {
        '1': {},
        '2': { '3': 1 },
        '3': { '2': 1, '6': 1, '9': 1, '5': 2, '10': 2, '8': 1 },
        '4': { '5': 1 },
        '5': { '4': 1,  '11': 1, '9': 1 },
        '6': { '3': 1 },
        '7': {},
        '8': { '9': 1, '11': 1},
        '9': {},
        '10': {},
        '11': {},
        '12': {} 
    }
    import_id = json.loads(resp_post.text)['import_id']
    resp_get = requests.get(f'http://localhost:8000/imports/{import_id}/citizens/birthdays')

    if resp_get.status_code != 201:
        print('ERR')

    birtdays = json.loads(resp_get.text)['data']
    for month, data in birtdays.items():
        if len(data) != len(excepted[month]):
            print('ERR')
            return 
        for item in data:
            if excepted[month][str(item["citizen_id"])] != item["presents"]:
                print('ERR')
                return
    print(f'OK  {resp_get.status_code} just ok')


def simple_test():
    n = 1000
    print(f'BEGIN simple test\nSAMPLE size={n}')
    data = sample.create(n)

    # POST sample
    start = time.time()
    resp_post = requests.post(
        'http://localhost:8000/imports', data=json.dumps(data))
    post_time = time.time() - start
    print(post_time)
    if resp_post.status_code != 201:
        print(f'ERR {resp_post.status_code} {resp_post.text}')
        return

    import_id = json.loads(resp_post.text)['import_id']
    print(f'IMPORT_ID {import_id}')
    # GET sample
    resp_get = requests.get(f'http://localhost:8000/imports/{import_id}')

    if resp_get.status_code != 201:
        print(f'ERR {resp_get.status_code} {resp_get.text}')
        return

    returned_data = json.loads(resp_get.text)
    if not helper.sample_equivalent(data, returned_data):
        print('ERR --- posted and getted samples not equivalent')
    else:
        print('OK ---')


if __name__ == '__main__':
    simple_test()
    print()
    validation_test_pack()
    print()
    patch_test()
    print()
    birtdays_test()
