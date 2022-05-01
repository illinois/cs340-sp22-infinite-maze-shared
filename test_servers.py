from servers import ServerManager

db_name = 'cs240-test-db' # use different db to avoid messing the main db
serverManager = ServerManager(db_name)
name = 'testMG'

def Log():
    print("Servers")
    print(serverManager.servers)

def setup():
    serverManager.connection.db.servers.delete_many({}) # start with empty db
    serverManager.load() # reset cache

def test():
    setup()

    assert(not serverManager.has_servers())
    assert(serverManager.find(name) is None)

    status, message = serverManager.insert({
        "name": name,
        "url": "http://localhost:24000",
        "author": "Aarya",
        "weight": 1
    })

    if status // 100 != 2:
        assert(len(serverManager.servers) == 0)
        assert(len(serverManager.names) == 0)
        assert(len(serverManager.weights) == 0)

        print(message)
        exit(1)

    Log()

    assert(serverManager.find('testMG') is not None)

    mg = serverManager.find(name)

    assert(bool(mg))
    assert('name' in mg)
    assert('author' in mg)
    assert('url' in mg)
    assert('weight' in mg)
    assert(len(serverManager.servers) == 1)
    assert(serverManager.names[0] == mg['name'])
    assert(serverManager.weights[0] == mg['weight'])

    status, message = serverManager.insert({
        "name": 'test2',
        "url": "http://localhost:24001",
        "author": "Aarya",
        "weight": 1
    })

    if status // 100 != 2:
        print(message)
        exit(1)

    assert(len(serverManager.servers) == 2)
    assert(len(serverManager.names) == 2)
    assert(len(serverManager.weights) == 2)
    assert(serverManager.find('test2') is not None)

    Log()

    status, message = serverManager.update(name, {
        'name': 'test1',
        'weight': 0.75,
        'author': 'aaryab2'
    })

    if status // 100 != 2:
        print(message)
        exit(1)

    mg = serverManager.find('test1')

    assert(serverManager.find(name) is None)
    assert(mg is not None)

    assert(mg['author'] == 'aaryab2')
    assert(mg['weight'] == 0.75)

    Log()

    assert(serverManager.names[0] == mg['name'])
    assert(serverManager.weights[0] == mg['weight'])

    status, message = serverManager.remove('test1')

    if status // 100 != 2:
        print(message)
        exit(1)

    assert(len(serverManager.servers) == 1)
    assert(len(serverManager.names) == 1)
    assert(len(serverManager.weights) == 1)
    assert(serverManager.find('test1') is None)

    mg = serverManager.find('test2')
    assert(serverManager.names[0] == mg['name'])
    assert(serverManager.weights[0] == mg['weight'])

    Log()

if __name__ == '__main__':
    test()