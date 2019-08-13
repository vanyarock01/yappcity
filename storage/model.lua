
local citzen = {
    pos = {
        citizen_id = 1,
        town       = 2,
        street     = 3,
        building   = 4,
        apartment  = 5,
        name       = 6,
        gender     = 7,
        relatives  = 8,
        birth_d    = 9,
        birth_m    = 10,
        birth_y    = 11
    },
    format = {
        { 'citizen_id',  'unsigned' },
        { 'town',        'string'   },
        { 'street',      'string'   },
        { 'building',    'string'   },
        { 'apartment',   'unsigned' },
        { 'name',        'string'   },
        { 'gender',      'string'   },
        { 'relatives',   'array'    },
        { 'birth_d',     'unsigned' },
        { 'birth_m',     'unsigned' },
        { 'birth_y',     'unsigned' }
    },
    indexes = {
        {
            name = 'primary',
            options = {
                type = 'HASH',
                parts = {1, 'unsigned'}
            }
        }
    }
}

return citzen
