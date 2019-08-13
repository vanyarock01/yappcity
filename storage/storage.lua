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

local sample = {}

function sample.check(name)
    if box.space[name] == nil then
        return false
    else
        return true
    end
end

function sample.create(data)
    local id = box.sequence.counter:next()
    local space_name = tostring(id)

    local space = box.schema.space.create(space_name, { format = model.format })
    for _, index in pairs(model.indexes) do
        space:create_index(index.name, index.options)
    end

    for _, citzen in pairs(data) do
        log.info(tostring(citzen))
        space:insert { unpack(citzen) }
    end

    return id
end

function sample.update_citizens(sample_id, citizen_pack)
    -- return info about first citizen
    local citizen = citizen_pack[1]
    local updated_citizen = box.space[sample_id]:update(citizen[1], citizen[2])
    -- update relative citizens, if exist
    for i = 2, #citizen_pack do
        citizen = citizen_pack[i]
        box.space[sample_id]:update(citizen[1], citizen[2])
    end
    return updated_citizen
end

function sample.citizen_with_relative(sample_id, citizen_id, new_relatives)
    -- return table - {citizen data, relatives data}
    local space_name = tostring(sample_id)

    -- TODO: remove this condition
    if not sample.check(space_name) then
        return false
    end
    local citizen = box.space[space_name]:get(citizen_id)
    -- collecting and inserting relatives data
    local citizen_relatives = {}
    for _, i in pairs(citizen[model.pos.relatives]) do
        table.insert(citizen_relatives, box.space[space_name]:get(i))
    end
    -- collecting new relaties data
    for _, i in pairs(new_relatives) do
        if not array_contains(citizen[model.pos.relatives], i) then
            table.insert(citizen_relatives, box.space[space_name]:get(i))
        end
    end

    return { citizen, citizen_relatives }
end

function sample.all(sample_id)
    local space_name = tostring(sample_id)
    -- TODO: remove this condition
    if not sample.check(space_name) then
        return false
    end

    local sample = {}
    
    for _, tuple in
        box.space[space_name].index.primary:pairs(nil, {
            iterator = box.index.ALL}) do

        table.insert(sample, tuple:totable())
    end
    return sample
end

local function init()
    box.schema.user.grant('guest',
            'create,read,write,execute',
            'universe',
            nil, { if_not_exists = true })

    box.schema.sequence.create('counter', { min = 0, start = 0 })

    rawset(_G, 'sample_create',                sample.create)
    rawset(_G, 'sample_update_citizens',       sample.update_citizens)
    rawset(_G, 'sample_all',                   sample.all)
    rawset(_G, 'sample_check',                 sample.check)
    rawset(_G, 'sample_citizen_with_relative', sample.citizen_with_relative)

end

box.cfg {
    listen     = conf.listen,
    log_format = conf.log_format,
    log        = conf.log_file,
    background = conf.back,
    pid_file   = conf.pid
}

init()
