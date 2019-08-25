import pytest
import requests
import json
import helper
from datetime import date



@pytest.fixture
def valid_data():
    return [
        (
            'simple data',
            {'citizens': [
                {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [2, 3], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
                {'citizen_id': 3, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
            ]}
        )
    ]


def test_valid(valid_data):
    for msg, data in valid_data:
        resp_get = requests.post(
            f'{helper.host}/imports', data=json.dumps(data), timeout=10)
        assert resp_get.status_code == 201, msg


@pytest.fixture
def invalid_data():
    today = date.today()
    future_date = f"{today.day}.{today.month}.{today.year + 1}"
    return [
        (
            'missing field town',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [], 'birth_date': '21.04.1960'}
            ]}
        ), (
            'invalid field citizen_id type',
            {'citizens': [
                {'citizen_id': '1', 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [], 'birth_date': '21.04.1960'}
            ]}
        ), (
            'Repeated citizen_id',
            {'citizens': [
                {'citizen_id': 1, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [], 'birth_date': '21.04.1960'},
                {'citizen_id': 2, 'street': 'n', 'town': 'm', 'building': 'n', 'apartment': 1,
                 'name': 'k', 'gender': 'female', 'relatives': [], 'birth_date': '22.04.1960'}
            ]}
        ), (
            'invalid relatives',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
                {'citizen_id': 3, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
            ]}
        ), (
            'invalid relatives types',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '20.04.1960'},
                {'citizen_id': 2, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [1], 'birth_date': '21.04.1960'},
                {'citizen_id': 3, 'street': 's', 'town': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [1], 'birth_date': '22.04.1960'}
            ]}
        ), (
            'invalid field name',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'city': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '20.04.1960'}
            ]}
        ), (
            'invalid date format',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'city': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': '1960/20/5'}
            ]}
        ), (
            'invalid date - future',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'city': 's', 'building': 's', 'apartment': 1,
                 'name': 's', 'gender': 'female', 'relatives': [3], 'birth_date': future_date}
            ]}
        ), (
            'invalid name - empty string',
            {'citizens': [
                {'citizen_id': 1, 'street': 's', 'city': 's', 'building': 's', 'apartment': 1,
                 'name': '', 'gender': 'female', 'relatives': [3], 'birth_date': '20.05.1992'}
            ]}
        )
    ]


def test_invalid(invalid_data):
    for msg, data in invalid_data:
        resp_get = requests.post(
            f'{helper.host}/imports', data=json.dumps(data), timeout=10)
        assert resp_get.status_code == 400, msg
