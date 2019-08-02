local model = require('model')
local conf = require('config')
local log = require('log')

local sample = {}

function sample.create(id)
    if box.space[id] ~= nil then
        return false
    end
    local space = box.schema.space.create(id, { format = model.format })
    for _, index in pairs(model.indexes) do
        space:create_index(index.name, index.options)
    end
    return true
end

function sample.insert(id, data)
    if box.space[id] == nil then
        return false
    end
    local note = box.space[id]:insert { unpack(data) }
    return note
end

function sample.all(id)
    if box.space[id] == nil then
        return false
    end

    local sample = {}
    
    for _, tuple in
        box.space[id].index.primary:pairs(nil, {
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
