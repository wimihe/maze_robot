#coding:utf-8
#Created by weimi on 2018/2/7.

async def insert(db, data):
    result = await db.insert_one(data)
    if result.acknowledged:
        return result.inserted_id
    raise ValueError('add error')

async def insert_many(db, data_list):
    result = await db.insert_many(data_list)
    if result.acknowledged:
        return result.inserted_ids
    raise ValueError('add_many error')

async def update(db, filter, data):
    result = await db.update_one(filter, {'$set': data})
    if result.acknowledged:
        return result.modified_count
    return False

async def update_many(db, data):
    result = await db.update_many(filter, {'$set': data})
    if result.acknowledged:
        return result.modified_count
    return False

async def find_one(db, filter):
    result = await db.find_one(filter)
    return result

async def find(db, filter=None, sort=None, fields=None, page=1, page_size=3000):
    kwargs = {}
    if filter:
        kwargs['filter'] = filter
    if sort:
        if isinstance(sort, dict):
            sort = [(key, sort[key]) for key in sort.keys()]
        kwargs['sort'] = sort
    if fields:
        kwargs['projection'] = fields

    result = db.find(**kwargs)

    total = await result.count()

    if page > 0 and page_size > 0:
        limit = page_size
        skip = (page - 1) * page_size
        result = result.limit(limit).skip(skip)
    else:
        limit = total

    return total, await result.to_list(limit)

