#!/usr/bin/env python3

import asyncio

from network import client, server, keys

async def test_001():

    server_001 = server.Server()
    await server_001.start()

    client_001 = client.Client()
    await client_001.start()
    assert client_001.data_session is None

    client_002 = client.Client()
    await client_002.start()
    assert client_002.data_session is None

    client_003 = client.Client()
    await client_003.start()
    assert client_003.data_session is None

    arguments = {
        keys.HOST: '127.0.0.1', # default host
        keys.PORT: 55000, # default port
    }

    arguments[keys.NAME_USER] = 'anonymous1'
    user_001 = await client_001.connect(**arguments)
    number_user_001 = user_001[keys.NUMBER_USER]
    assert client_001.data_session is not None

    arguments[keys.NAME_USER] = 'anonymous2'
    user_002 = await client_002.connect(**arguments)
    number_user_002 = user_002[keys.NUMBER_USER]
    assert client_002.data_session is not None

    arguments[keys.NAME_USER] = 'anonymous3'
    user_003 = await client_003.connect(**arguments)
    number_user_003 = user_003[keys.NUMBER_USER]
    assert client_003.data_session is not None

    users_data_map = await client_001.users_request()

    list_users_numbers_a = [
        number_user_001,
        number_user_002,
        number_user_003,
    ]

    set_users_numbers_a = set(list_users_numbers_a)

    list_users_numbers_b = []

    for user_data in users_data_map.values():

        number_user = user_data[keys.NUMBER_USER]
        list_users_numbers_b.append(number_user)

    set_users_numbers_b = set(list_users_numbers_b)

    # the only users logged-in should be the ones we have created here
    assert set_users_numbers_a == set_users_numbers_b

    list_users_names_a = [
        'anonymous1',
        'anonymous2',
        'anonymous3',
    ]

    set_users_names_a = set(list_users_names_a)

    list_users_names_b = []

    for user_data in users_data_map.values():

        name_user = user_data[keys.NAME_USER]
        list_users_names_b.append(name_user)

    set_users_names_b = set(list_users_names_b)

    # the names received from the server should be the same that we gave to it.
    assert set_users_names_a == set_users_names_b

    number_client_001 = client_001.data_session[keys.NUMBER_USER]
    number_client_002 = client_002.data_session[keys.NUMBER_USER]

    number_session_001 = client_001.data_session[keys.NUMBER_SESSION]
    number_session_002 = client_002.data_session[keys.NUMBER_SESSION]

    message = 'Hello, World!'        

    arguments = {
        keys.NUMBER_USER: number_client_002,
        keys.MESSAGE: message,
    }

    message_delivered = await client_001.send_message(**arguments)
    assert message_delivered is True

    assert number_client_001 in client_002.chat_histories

    chat_history_002_001 = client_002.chat_histories[number_client_001]

    assert chat_history_002_001[0] == message

    message = 'Echo!'

    arguments = {
        keys.NUMBER_USER: number_client_002,
        keys.MESSAGE: message,
    }

    message_delivered = await client_001.broadcast_message(**arguments)

    # small delay to allow for the broadcast messsage to reach all users
    await asyncio.sleep(2)

    chat_history_003_001 = client_003.chat_histories[number_client_001]

    assert chat_history_003_001[0] == message

    server_001.close()
    client_001.close()
    client_002.close()
    client_003.close()

async def main():

    await test_001()
    print('test_001 passed')

# asyncio setup
coroutine_main = main()
asyncio.run(coroutine_main)
