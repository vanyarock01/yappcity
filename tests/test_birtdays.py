import pytest
import requests
import json
import helper

host = 'http://localhost:8000'


@pytest.fixture(scope="module")
def post_data():
    data = {
        'citizens': [
            {
                'citizen_id': 1,
                'relatives': [],
                'birth_date': '03.01.1960'
            },
            {
                'citizen_id': 2,
                'relatives': [3],
                'birth_date': '05.02.1960'
            },
            {
                'citizen_id': 3,
                'relatives': [2, 6],
                'birth_date': '22.03.1960'
            },
            {
                'citizen_id': 4,
                'relatives': [5],
                'birth_date': '05.04.1960'
            },
            {
                'citizen_id': 5,
                'relatives': [4, 11, 9],
                'birth_date': '12.05.1960'
            },
            {
                'citizen_id': 6,
                'relatives': [3],
                'birth_date': '22.06.1980'
            },
            {
                'citizen_id': 7,
                'relatives': [],
                'birth_date': '22.04.1960'
            },
            {
                'citizen_id': 8,
                'relatives': [9],
                'birth_date': '22.03.1970'
            },
            {
                'citizen_id': 9,
                'relatives': [5, 8, 10],
                'birth_date': '21.03.1960'
            },
            {
                'citizen_id': 10,
                'relatives': [9, 11],
                'birth_date': '22.08.1960'
            },
            {
                'citizen_id': 11,
                'relatives': [5, 10],
                'birth_date': '22.03.1960'
            }
        ]}
    for citizen in data['citizens']:
        # adding default values ​​to missing fields
        citizen['street'] = 's'
        citizen['town'] = 's'
        citizen['building'] = 's'
        citizen['apartment'] = 1
        citizen['name'] = 'name'
        citizen['gender'] = 'female'

    resp_post = requests.post(f'{host}/imports', data=json.dumps(data), timeout=10)
    return json.loads(resp_post.text)

def test_birthdays(post_data):
    excepted = {
        '1': {},
        '2': {
            '3': 1
        },
        '3': {
            '2': 1,
            '6': 1,
            '9': 1,
            '5': 2,
            '10': 2,
            '8': 1
        },
        '4': {
            '5': 1
        },
        '5': {
            '4': 1,
            '11': 1,
            '9': 1
        },
        '6': {
            '3': 1
        },
        '7': {},
        '8': {
            '9': 1,
            '11': 1
        },
        '9': {},
        '10': {},
        '11': {},
        '12': {}
    }

    import_id = post_data['import_id']
    resp_get = requests.get(f'{host}/imports/{import_id}/citizens/birthdays', timeout=10)
    assert resp_get.status_code == 201

    birtdays = json.loads(resp_get.text)['data']
    for month, data in birtdays.items():
        assert len(data) == len(excepted[month])
        for item in data:
            assert excepted[month][str(item["citizen_id"])] == item["presents"]
