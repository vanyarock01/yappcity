local model = require('model')
local conf = require('config')
local log = require('log')

function array_contains(array, value, key)
    if not array then
        return false
    end
    local key = key or function(x) return x end
    for _, v in ipairs(array) do
        if key(v) == value then
            return true
        end
    end

    return false
end

local import = {}

function import.create(data)
    local id = box.sequence.counter:next()
    local space_name = tostring(id)

    local space = box.schema.space.create(space_name, { format = model.format })
    for _, index in pairs(model.indexes) do
        space:create_index(index.name, index.options)
    end

    for _, citzen in pairs(data) do
        space:insert { unpack(citzen) }
    end

    return id
end

local function space_by_import_id(import_id)
    return box.space[tostring(import_id)]
end

function import.update_citizens(import_id, citizen_pack)
    -- return info about first citizen

    local import_space = space_by_import_id(import_id)

    if import_space == nil then
        return nil
    end
    
    local citizen = citizen_pack[1]
    local updated_citizen = import_space:update(citizen[1], citizen[2])
    -- update relative citizens, if exist
    for i = 2, #citizen_pack do
        citizen = citizen_pack[i]
        import_space:update(citizen[1], citizen[2])
    end
    return updated_citizen
end

function import.citizen_with_relative(import_id, citizen_id, new_relatives)
    -- return table - {citizen data, relatives data}
    local import_space = space_by_import_id(import_id)

    if import_space == nil then
        return nil
    end

    local citizen = import_space:get(citizen_id)
    -- collecting and inserting relatives data
    local citizen_relatives = {}
    for _, i in pairs(citizen[model.pos.relatives]) do
        table.insert(citizen_relatives, import_space:get(i))
    end
    -- collecting new relaties data
    for _, i in pairs(new_relatives) do
        if not array_contains(citizen[model.pos.relatives], i) then
            table.insert(citizen_relatives, import_space:get(i))
        end
    end

    return { citizen, citizen_relatives }
end

function import.birthdays(import_id)
    local import_space = space_by_import_id(import_id)

    if import_space == nil then
        return nil
    end

    local birth_data = {}
    for month = 1, 12 do

        local month_data = {}
        for _, tuple in
                import_space.index.birthdays:pairs({month}, {iterator='EQ'} ) do

            for _, citzen_id in pairs(tuple[model.pos.relatives]) do
                local citizen_id_str = tostring(citzen_id)
                
                if month_data[citizen_id_str] == nil then
                    month_data[citizen_id_str] = 0
                end

                month_data[citizen_id_str] = month_data[citizen_id_str] + 1
            end
        end
        birth_data[tostring(month)] = month_data
    end
    return birth_data
end


function import.towns_ages(import_id)
    local import_space = space_by_import_id(import_id)

    if import_space == nil then
        return nil
    end

    local cur_date = os.date("*t")
    
    local get_age = function(day, month, year)
        local age = cur_date.year - year
        if month > cur_date.month or
                month == cur_date.month and day > cur_date.day then
            age = age - 1
        end

        return age
    end

    local town_data = {}
    for _, tuple in import_space:pairs() do
        local town = tuple[model.pos.town]
        if town_data[town] == nil then
            town_data[town] = {}
        end
        local age = get_age(
            tuple[model.pos.birth_d],
            tuple[model.pos.birth_m],
            tuple[model.pos.birth_y])

        table.insert(town_data[town], age)
    end

    return town_data
end

function import.all(import_id)
    local import_space = space_by_import_id(import_id)

    if import_space == nil then
        return nil
    end

    local import = {}
    
    for _, tuple in
        import_space.index.primary:pairs(nil, {
            iterator = box.index.ALL}) do

        table.insert(import, tuple:totable())
    end
    return import
end

local function init()
    box.schema.user.grant('guest',
            'create,read,write,execute',
            'universe',
            nil, { if_not_exists = true })

    if box.sequence.counter == nil then
        box.schema.sequence.create('counter', { min = 0, start = 0 })
    end
    
    for name, func in pairs(import) do
        rawset(_G, 'import_' .. name, func)        
    end
end

box.cfg {
    listen     = conf.listen,
    log_format = conf.log_format,
    log        = conf.log_file,
    background = conf.back,
    pid_file   = conf.pid
}

init()
