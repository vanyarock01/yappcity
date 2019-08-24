import pytest
import requests
import json
import sample
import helper
import threading


host = 'http://localhost:8000'

def background_post_get(import_data):
    resp_post = requests.post(
        f'{host}/imports', data=json.dumps({
            'citizens': import_data
        }), timeout=10.0)

    assert resp_post.status_code == 201

    import_id = json.loads(resp_post.text)['data']['import_id']
    assert isinstance(import_id, int) == True

    resp_get = requests.get(
        f'{host}/imports/{import_id}/citizens', timeout=10.0)
    assert resp_get.status_code == 200

    resp_data = json.loads(resp_get.text)
    assert helper.sample_equivalent(resp_data['data'], import_data)


def test_post_get():
    count = 30
    imports = [sample.create(1000) for _ in range(count)]

    treads = []

    for data in imports:
        treads.append(threading.Thread(
            target=background_post_get, args=(data,)))

    for tread in treads:
        tread.start()

    for tread in treads:
        tread.join()


def background_patch(import_id, data_pack):
    for i, data in data_pack:
        resp_patch = requests.patch(
            f'{host}/imports/{import_id}/citizens/{i}',
            data=json.dumps(data), timeout=10)
        assert resp_patch.status_code == 200


def test_patch():
    k = 10000
    data = sample.create(k)

    resp_post = requests.post(
        f'{host}/imports', data=json.dumps({
            'citizens': data
        }), timeout=10.0)

    import_id = json.loads(resp_post.text)['data']['import_id']

    new_data = sample.create(k)
    data_pack = []
    
    k = 0
    while k < len(new_data):
        pack = []
        for i in range(10):
            pack.append((
                new_data[k]['citizen_id'], {
                    'relatives': new_data[k]['relatives']
                }
            ))
            k += 1    
        data_pack.append(pack)


    treads = [] 
    pack_len = 10
    for i in range(len(data_pack)):
        treads.append(threading.Thread(
            target=background_patch, args=(import_id, data_pack[i])))

    for tread in treads:
        tread.start()

    for tread in treads:
        tread.join()
    
    resp_get = requests.get(
        f'{host}/imports/{import_id}/citizens', timeout=10.0)

    assert resp_get.status_code == 200

    resp_data = json.loads(resp_get.text)
    for citizen in resp_data['data']:
        i = citizen['citizen_id']
        assert set(citizen['relatives']) == set(new_data[i]['relatives'])

