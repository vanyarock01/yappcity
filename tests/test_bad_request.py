import pytest
import requests
import json
import helper

def test_empty_data_on_post():
    resp_get = requests.post(
        f'{helper.host}/imports', data=json.dumps({}), timeout=10)
    assert resp_get.status_code == 400


def test_empty_citizen_list_on_post():
    resp_get = requests.post(
        f'{helper.host}/imports', data=json.dumps({'citizen': []}), timeout=10)
    assert resp_get.status_code == 400


def test_bad_data_on_post():
    resp_get = requests.post(
        f'{helper.host}/imports', data=json.dumps({'bad': []}), timeout=10)
    assert resp_get.status_code == 400


def test_bad_json_on_post():
    resp_get = requests.post(
        f'{helper.host}/imports', data='bad json', timeout=10)
    assert resp_get.status_code == 400


def test_check_type_params_patch_type():
    resp_get = requests.patch(
        f'{helper.host}/imports/string/citizens/1', data = json.dumps({}))
    assert resp_get.status_code == 404 # endpoint not found


def test_check_type_params_patch_value():
    resp_get = requests.patch(
        f'{helper.host}/imports/-1/citizens/1', data = json.dumps({}))
    assert resp_get.status_code == 404 # endpoint not found


def test_bad_patch_body_empty():
    resp_get = requests.patch(
        f'{helper.host}/imports/1/citizens/1', data = json.dumps({}))
    assert resp_get.status_code == 400 # endpoint not found

def test_bad_patch_body_type_list():
    resp_get = requests.patch(
        f'{helper.host}/imports/1/citizens/1', data = json.dumps([]))
    assert resp_get.status_code == 400 # endpoint not found

def test_bad_patch_body_type_string():
    resp_get = requests.patch(
        f'{helper.host}/imports/1/citizens/1', data = json.dumps('str'))
    assert resp_get.status_code == 400 # endpoint not found
