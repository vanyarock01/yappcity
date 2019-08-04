
local citzen = {
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
