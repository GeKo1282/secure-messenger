from scripts.cypher import Cipher
from scripts.WebServer import HTTP_Server
import asyncio

server = HTTP_Server()

if __name__ == "__main__":
    def start_asyncio():
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_forever()

    server.run()
    start_asyncio()
