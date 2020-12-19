import asyncio
import logging
import uuid
import websockets

from game import Game


class ClientConnection:
    def __init__(self, socket):
        self.uuid = uuid.uuid4()
        self.socket = socket
        self.nickname = 'default nickname'
        self.game = None
        self.hand_cards = []

    async def send_message(self, msg):
        logging.debug(f'{self.uuid} - sending message to client: {msg}')
        await self.socket.send(msg)


class Lobby:
    def __init__(self):
        self.connections = []

    async def add_connection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)
            await connection.send_message('<lobby>: waiting')

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def get_players(self, num):
        if len(self.connections) < num:
            return None
        return [self.connections.pop(0) for _ in range(num)]

    def __len__(self):
        return len(self.connections)


lobby = Lobby()
games = []
PLAYERS_PER_GAME = 2


async def server(websocket, path):
    global games
    global lobby
    global PLAYERS_PER_GAME

    con = ClientConnection(websocket)
    logging.info(f'{con.uuid} - connection established; path: {path}')

    while True:
        data = (await websocket.recv()).decode('utf-8').strip()
        logging.debug(f'{con.uuid} - received data: {data}')

        if data.startswith('<nickname>: '):
            con.nickname = data[12:]
            if not con.game:
                await lobby.add_connection(con)
                logging.debug(f'{con.uuid} - adding to lobby')
                if len(lobby) >= PLAYERS_PER_GAME:
                    games.append(Game(lobby.get_players(PLAYERS_PER_GAME)))
            else:
                await con.send_message('you are already in a game')
        elif data == 'this is my turn':
            await con.game.turn(con)
            logging.debug(f'{con.uuid} - received turn')
        elif data == 'quit':
            logging.debug(f'{con.uuid} - received quit command')
            break

    if con.game is not None:
        con.game.quit_game()
    else:
        lobby.remove_connection(con)

    logging.info(f'{con.uuid} - closing connection')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    start_server = websockets.serve(server, "localhost", 10001)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    logging.info('server started on port 10001')
