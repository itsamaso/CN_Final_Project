import asyncio

from network import server

MAIN_SLEEP = 5 # seconds

# main method for server
async def main():

    main_server = server.Server()
    await main_server.start()

    while True:

        # sleeps in order to let other tasks run
        await asyncio.sleep(MAIN_SLEEP)

        # calls garbage collection (disconnected users, dropped sessions)
        main_server.helper_janitor()

coroutine_main = main()
asyncio.run(coroutine_main)
