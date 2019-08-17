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