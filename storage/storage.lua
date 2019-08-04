local model = require('model')
local conf = require('config')
local log = require('log')

local sample = {}

function sample.insert(id, data)
    if box.space[id] == nil then
        return false
    end
    local note = box.space[id]:insert { unpack(data) }
    return note
end

function sample.create(data)
    local id = box.sequence.counter:next()
    local space_name = tostring(id)

    if box.space[space_name] ~= nil then
        return false
    end
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


function sample.all(id)
    local space_name = tostring(id)
    if box.space[space_name] == nil then
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

    rawset(_G, 'sample_create', sample.create)
    rawset(_G, 'sample_insert', sample.insert)
    rawset(_G, 'sample_all',    sample.all)
end

box.cfg {
    listen     = conf.listen,
    log_format = conf.log_format,
    log        = conf.log_file,
    background = conf.back,
    pid_file   = conf.pid
}

init()
