import pytest
import requests
import json
import sample
import helper

host = 'http://localhost:8000'


@pytest.fixture(scope="module")
def post_data():
    resp_post = requests.post(
        f'{host}/imports',
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
        ),
        timeout=10)

    return json.loads(resp_post.text)['data']


def test_invalid(post_data):
    invalid_data = {
        'citizen_id': 2,
        'apartment': 1,
    }
    resp_patch = requests.patch(
        f'{host}/imports/{post_data["import_id"]}/citizens/1',
        data=json.dumps(invalid_data), timeout=10)

    assert resp_patch.status_code == 400, 'try change citizen_id field'


def test_patch(post_data):
    # patch citizen without relatives
    patch_data = {
        'town': 'Moscow',
        'birth_date': '21.05.1970',
        'name': 'Dasha',
        'apartment': 2
    }
    resp_patch = requests.patch(
        f'{host}/imports/{post_data["import_id"]}/citizens/1',
        data=json.dumps(patch_data), timeout=10)

    assert resp_patch.status_code == 200, 'patch 1 citizen'

    excepted_first = {
        'citizen_id': 1,
        'street': 'n',
        'town': 'Moscow',
        'building': 'n',
        'apartment': 2,
        'name': 'Dasha',
        'gender': 'female',
        'relatives': [2, 3, 4],
        'birth_date': '21.05.1970'
    }
    assert helper.citizen_equivalent(
        excepted_first, json.loads(resp_patch.text)['data']) == True, 'patch citizen data'

    # patch citizen with relatives

    insert_relatives = {
        'relatives': [1, 2]
    }

    resp_patch = requests.patch(
        f'{host}/imports/{post_data["import_id"]}/citizens/3',
        data=json.dumps(insert_relatives), timeout=10)
    assert resp_patch.status_code == 200, 'add citizen with id == 2 to relatives citizen with id == 3'

    excepted_third = {
        'citizen_id': 3,
        'street': 'n',
        'town': 'm',
        'building': 'n',
        'apartment': 1,
        'name': 'k',
        'gender': 'female',
        'relatives': [1, 2],
        'birth_date': '22.04.1960'
    }
    assert helper.citizen_equivalent(
        excepted_third, json.loads(resp_patch.text)['data']) == True, 'insert relatives'

    remove_relatives = {
        'relatives': [1]
    }

    resp_patch = requests.patch(
        f'{host}/imports/{post_data["import_id"]}/citizens/4',
        data=json.dumps(remove_relatives), timeout=10)
    assert resp_patch.status_code == 200, 'remove citizen with id == 2 to relatives citizen with id == 4'

    excepted_fourth = {
        'citizen_id': 4,
        'street': 'n',
        'town': 'm',
        'building': 'n',
        'apartment': 1,
        'name': 'k',
        'gender': 'female',
        'relatives': [1],
        'birth_date': '22.04.1960'
    }
    assert helper.citizen_equivalent(
        excepted_fourth, json.loads(resp_patch.text)['data']) == True, 'remove relatives'

    # compare all sample with excepted

    resp_get = requests.get(
        f'{host}/imports/{post_data["import_id"]}/citizens', timeout=10)
    assert resp_get.status_code == 200

    excepted_second = {
        'citizen_id': 2,
        'street': 'n',
        'town': 'm',
        'building': 'n',
        'apartment': 1,
        'name': 'k',
        'gender': 'female',
        'relatives': [1, 3],
        'birth_date': '21.04.1960'
    }

    excepted_sample = [
        excepted_first,
        excepted_second,
        excepted_third,
        excepted_fourth
    ]

    assert helper.sample_equivalent(
        json.loads(resp_get.text)['data'], excepted_sample) == True, 'compare all sample with excepted'

@pytest.fixture
def big_post_data():
    return sample.create(10000)

def test_patch_all_relatives_timeout(big_post_data):
    resp_post = requests.post(
        f'{host}/imports', data=json.dumps({
            'citizens': big_post_data
        }), timeout=10.0)

    assert resp_post.status_code == 201

    import_id = json.loads(resp_post.text)['data']['import_id']

    # update citizen: add to relative all other citizen
    patch_data = {
        'relatives': []
    }

    i = len(big_post_data) - 1
    for k in range(i):
        patch_data['relatives'].append(k)

    resp_patch = requests.patch(
        f'{host}/imports/{import_id}/citizens/{i}',
        data=json.dumps(patch_data), timeout=10)

    assert resp_patch.status_code == 200

