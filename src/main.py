import asyncio
import logging
import websockets

from client_connection import ClientConnection
from game import Game
from lobby import Lobby


HOST = "localhost"
PORT = 10001
PLAYERS_PER_GAME = 2

lobby = Lobby()
games = []


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

    start_server = websockets.serve(server, HOST, PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    logging.info(f'server started on {HOST}:{PORT}')
