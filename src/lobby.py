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
