import pytest
import requests
import json
import sample
import helper

host = 'http://localhost:8000'


@pytest.fixture
def import_data():
    return sample.create(100)


def test_post_get(import_data):
    # try POST data
    resp_post = requests.post(
        f'{host}/imports', data=json.dumps(import_data), timeout=10.0)
    assert resp_post.status_code == 201

    import_id = json.loads(resp_post.text)['import_id']
    assert isinstance(import_id, int) == True
    
    # try GET data
    resp_get = requests.get(
        f'{host}/imports/{import_id}', timeout=10.0)
    assert resp_get.status_code == 201

    resp_data = json.loads(resp_get.text)
    assert helper.sample_equivalent(resp_data, import_data)
