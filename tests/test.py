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


def simple_test():
    n = 10000
    print(f'SAMPLE SIZE {n}')
    data = sample.create(n)

    # POST sample
    start = time.time()
    resp_post = requests.post(
        'http://localhost:8000/imports', data=json.dumps(data))
    print(f'EXEC TIME POST: {time.time() - start}')

    assert resp_post.status_code == 201
    import_id = json.loads(resp_post.text)
    
    # GET sample
    start = time.time()
    resp_get = requests.get(f'http://localhost:8000/imports/{import_id}')
    print(f'EXEC TIME GET:  {time.time() - start}')

    assert resp_get.status_code == 201
    returned_data = json.loads(resp_get.text)

    if not sample_equivalent(data, returned_data):
        print('ERROR')
    else:
        print('OK')


if __name__ == '__main__':
    simple_test()
