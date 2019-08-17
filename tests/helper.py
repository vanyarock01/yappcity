from datetime import datetime, date
import numpy as np


def citizen_equivalent(x, y):
    for k, v in x.items():
        if k == 'relatives' and set(v) != set(y[k]):
            return False
        elif v != y[k]:
            return False
    return True


def sample_equivalent(x, y):
    """ very slow dict compare """

    for c1 in x['citizens']:
        finded = False
        for c2 in y['citizens']:
            finded = finded or citizen_equivalent(c1, c2)
        if not finded:
            return False
    return True


def get_age(d, m, y):
    today = date.today()
    age = today.year - y
    if m > today.month or (m == today.month and d > today.day):
        age -= 1
    return age


def calc_percentiles(citizens, p):
    towns = {}
    for citizen in citizens:
        if not towns.get(citizen['town']):
            towns[citizen['town']] = []
        birtday = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
        towns[citizen['town']].append(
            get_age(birtday.day, birtday.month, birtday.year))

    res = {}
    for town, ages in towns.items():
        res[town] = {}
        for val in p:
            res[town]['p'+str(val)] = int(np.percentile(np.array(ages), val))

    return res
