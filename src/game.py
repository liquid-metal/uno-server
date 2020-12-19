import asyncio
import logging
import random


class Game:
    def __init__(self, connections):
        self.connections = connections
        self.active_turn = None
        self.remaining_cards = []
        self.top_card = None

        self.fill_deck()

        for c in connections:
            c.hand_cards.extend([self.remaining_cards.pop() for _ in range(7)])
        self.top_card = self.remaining_cards.pop()

        for c in connections:
            asyncio.get_event_loop().create_task(c.send_message(
                f'<game>: {[x.nickname for x in connections]};{c.hand_cards};{self.top_card}'))
        # players are ready and out of the lobby - setup the game and notify them

    def fill_deck(self):
        # r g b y b 0-9 A=aussetzen, R=richtungswechsel, 2=2ziehen
        # s0 farbwunsch, s4=4ziehen
        self.remaining_cards = [f'r{i}' for i in range(10)]
        self.remaining_cards.extend([f'g{i}' for i in range(10)])
        self.remaining_cards.extend([f'b{i}' for i in range(10)])
        self.remaining_cards.extend([f'y{i}' for i in range(10)])
        self.remaining_cards.extend(['rA', 'rR', 'r2', 'gA', 'gR', 'g2', 'bA', 'bR', 'b2', 'yA', 'yR', 'y2',
                                     's0', 's0', 's4', 's4'])
        self.remaining_cards = [x for pair in zip(self.remaining_cards, self.remaining_cards) for x in pair]
        random.shuffle(self.remaining_cards)

    async def next_one(self):
        if len(self.connections) == 0:
            logging.debug('no active connection - setting active_turn to None')
            self.active_turn = None
        elif len(self.connections) == 1:
            logging.debug(f'only one active connection - setting active connection to {self.connections[0].uuid}')
            self.active_turn = self.connections[0]
        else:
            current_index = self.connections.index(self.active_turn)
            self.active_turn = self.connections[(current_index + 1) % len(self.connections)]
            logging.debug(f'setting active_turn to {self.active_turn.uuid}')
        await self.send_state()

    async def send_state(self):
        for c in self.connections:
            if c == self.active_turn:
                logging.debug(f'{c.uuid} - notifying about active turn')
                await c.socket.send('it is your turn')
            else:
                logging.debug(f'{c.uuid} - notifying about non-active turn')
                await c.socket.send('it is not your turn')

    async def turn(self, connection):
        if connection == self.active_turn:
            await connection.socket.send('thanks for your turn')
            await self.next_one()
        else:
            await connection.socket.send('CHEATER!')

    async def quit_game(self):
        # TODO
        pass
