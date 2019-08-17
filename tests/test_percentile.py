import pytest
import requests
import json
import helper

host = 'http://localhost:8000'


@pytest.fixture
def post_data():
    data = {
        'citizens': [
            {
                'citizen_id': 1,
                'town': 'Moscow',
                'birth_date': '03.01.1961'
            },
            {
                'citizen_id': 2,
                'town': 'Moscow',
                'birth_date': '05.02.1964'
            },
            {
                'citizen_id': 3,
                'town': 'Moscow',
                'birth_date': '22.03.2000'
            },
            {
                'citizen_id': 4,
                'town': 'Moscow',
                'birth_date': '05.04.2001'
            },
            {
                'citizen_id': 5,
                'town': 'Moscow',
                'birth_date': '12.05.1998'
            },
            {
                'citizen_id': 6,
                'town': 'Moscow',
                'birth_date': '22.06.1980'
            },
            {
                'citizen_id': 7,
                'town': 'Kursk',
                'birth_date': '22.04.1960'
            },
            {
                'citizen_id': 8,
                'town': 'Kursk',
                'birth_date': '22.03.1972'
            },
            {
                'citizen_id': 9,
                'town': 'Kursk',
                'birth_date': '21.03.1968'
            },
            {
                'citizen_id': 10,
                'town': 'Kursk',
                'birth_date': '22.04.1991'
            },
            {
                'citizen_id': 11,
                'town': 'Torzok',
                'birth_date': '22.03.2001'
            }
        ]}
    for citizen in data['citizens']:
        # adding default values ​​to missing fields
        citizen['relatives'] = []
        citizen['town'] = 's'
        citizen['street'] = 's'
        citizen['building'] = 's'
        citizen['apartment'] = 1
        citizen['name'] = 'name'
        citizen['gender'] = 'female'

    resp_post = requests.post(
        f'{host}/imports', data=json.dumps(data), timeout=10)
    return data, json.loads(resp_post.text)


def test_percentile(post_data):
    excepted_data = helper.calc_percentiles(
        post_data[0]['citizens'], [50, 75, 99])

    import_id = post_data[1]['import_id']
    resp_get = requests.get(
        f'{host}/imports/{import_id}/towns/stat/percentile/age', timeout=10)
    assert resp_get.status_code == 201

    data = json.loads(resp_get.text)['data']
    for town_stat in data:
        # try get excepted stats
        town = excepted_data.get(town_stat['town'])
        assert town != None, 'check town is exist'

        for p, v in town.items():
            assert v == town_stat[p], 'compare percentiles value'
