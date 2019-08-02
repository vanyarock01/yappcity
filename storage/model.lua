
local citzen = {
    format = {
        { 'citizen_id',  'unsigned' },
        { 'town',        'string'   },
        { 'street',      'string'   },
        { 'building',    'string'   },
        { 'appartement', 'unsigned' },
        { 'name',        'string'   },
        { 'birth_date',  'string'   },
        { 'gender',      'string'   },
        { 'relatives',   'array'    }
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
