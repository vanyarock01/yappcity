#!/usr/bin/env python3
import collections
import requests
import sample
import json
import time


def sample_equivalent(x, y):
    """ very slow dict compare """

    for c1 in x['citizens']:
        finded = False
        for c2 in y['citizens']:
            ok = True
            for k, v in c1.items():
                if k == 'relatives' and set(v) != set(c2[k]):
                    ok = False
                elif v != c2[k]:
                    ok = False
            if ok:
                finded = True
        if not finded:
            return False
    return True


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
                 'name': 'k', 'gender': 'female', 'relatives': [2, 3], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
                {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
            ]}
        ))

    if resp_post.status_code != 201:
        print(f'ERR {resp_post.status_code} {resp_post.text}')
        return

    import_id = json.loads(resp_post.text)['import_id']
    print(f'IMPORT_ID {import_id}')

    test_pack = []
    test_pack.append((
        1,
        requests.patch,
        'optional validation',
        201,
        {'town': 'm', 'building': 'n', 'apartment': 1,
         'name': 'k', 'birth_date': '20.04.1960'}
    ))

    test_pack.append((
        1,
        requests.patch,
        'optional validation with try update citzen_id',
        400,
        {'citizen_id': 1, 'town': 'm', 'building': 'n', 'apartment': 1,
         'name': 'k', 'birth_date': '20.04.1960'}
    ))

    for i, method, msg, code, data in test_pack:
        resp_test = method(
            f'http://localhost:8000/imports/{import_id}/citizens/{i}', data=json.dumps(data))
        result = 'OK '
        if resp_test.status_code != code:
            result = 'ERR'
        print(f'{result} {resp_test.status_code} {msg} ')


def simple_test():
    n = 100
    print(f'BEGIN simple test\nSAMPLE size={n}')
    data = sample.create(n)

    # POST sample
    start = time.time()
    resp_post = requests.post(
        'http://localhost:8000/imports', data=json.dumps(data))
    post_time = time.time() - start

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
    if not sample_equivalent(data, returned_data):
        print('ERR --- posted and getted samples not equivalent')
    else:
        print('OK ---')


if __name__ == '__main__':
    simple_test()
    print()
    validation_test_pack()
    print()
    patch_test()