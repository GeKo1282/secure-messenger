import json
from pathlib import Path
from scripts.cypher import Cipher
from scripts.WebServer import HTTP_Server
from scripts.logger import Logger
from scripts.database import Database
import asyncio

server_settings = json.load(open("./settings.json", "r"))
for path in server_settings['DIRS']:
    Path(path).mkdir(parents=True, exist_ok=True)
users = Database(server_settings['USERS_DATABASE_PATH'], 'users')
users.create_table("users",
                   {"uuid": "int UNIQUE NOT NULL", "email": "text UNIQUE NOT NULL", "password": "text NOT NULL",
                    "username": "text NOT NULL", "tag": "int NOT NULL", "email_verified": "boolean NOT NULL",
                    "verification_code": "text"})
cipher = Cipher()

logger = Logger(name="logger",
                datetime_format=server_settings['DATETIME_FORMAT'],
                level=server_settings['LOGGING_LEVEL'])
server = HTTP_Server(cipher, server_settings['HOSTNAME'], logger=logger)

if __name__ == "__main__":
    def start_asyncio():
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_forever()


    server.run()
    start_asyncio()


# TODO: Big ass fullscreen server/dm selector w/ squares spread as table
