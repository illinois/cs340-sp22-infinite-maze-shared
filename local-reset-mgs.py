import requests

middlewareURL = 'http://localhost:5000'

mgs = [{
    'name': 'random',
    'port': '24000'
}, {
    'name': 'oneblock',
    'port': '24004'
},
    {
    'name': 'target',
    'port': '24002'
}, {
    'name': 'fish',
    'port': '24003'
}, ]

from connection import Connection

connection = Connection(db_name='cs240-infinite-maze')
connection.db.servers.delete_many({})
connection.db.mazes.delete_many({})

for mg in mgs:
    data = {
        "name": mg['name'],
        "url" : f"http://localhost:{mg['port']}",
        "author":"aarya",
        "weight": 0.5
    }

    response = requests.put(f'{middlewareURL}/addMG', json=data)
    print(response.status_code)


response = requests.get(f'{middlewareURL}/log')

print(response.json())

