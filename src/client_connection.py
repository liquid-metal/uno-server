import logging
import uuid


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
