import json
import random

name_male = ['Иван', 'Никита', 'Вова', 'Олег',
             'Коля', 'Степа', 'Миша', 'Максим', 'Андрей']

name_female = ['Женя', 'Лена', 'Даша', 'Тоня',
               'Лиза', 'Юля', 'Настя', 'Света', 'Ульяна']

towns = ['Москва', 'Курск', 'Севастополь']
streets = ['default']
buildings = ['default']


def check(all_relatives):
    for i, relatives in all_relatives.items():
        for r in relatives:
            if i not in all_relatives[r]:
                return False
    return True


def create_citzen(i, relatives):
    citzen = {}

    citzen['citizen_id'] = i

    citzen['town'] = random.choice(towns)
    citzen['street'] = random.choice(streets)
    citzen['building'] = random.choice(buildings)
    citzen['apartment'] = random.randint(1, 500)

    gender = random.choice(['male', 'female'])

    if gender == 'male':
        citzen['name'] = random.choice(name_male)
    else:
        citzen['name'] = random.choice(name_female)

    day = random.randint(1, 25)
    month = random.randint(1, 12)
    year = random.randint(1950, 2018)

    citzen['birth_date'] = '{:02d}.{:02d}.{}'.format(day, month, year)
    citzen['gender'] = gender

    citzen['relatives'] = list(relatives)

    return citzen


def create(k=1000):
    indexes = list(range(k))

    all_relatives = {i: set() for i in indexes}
    for i in indexes:
        coef = random.randint(0, 10)
        relative_count = 1 if coef == 1 else 0 
        relatives = set(random.choices(
            indexes[:i] + indexes[i:], k=relative_count))
        all_relatives[i] |= relatives

        for j in relatives:
            all_relatives[j].add(i)

    if not check(all_relatives):
        print('Incorrect generation relatives')

    citizens = []

    for i, relatives in all_relatives.items():
        citizens.append(create_citzen(i, relatives))

    return citizens

