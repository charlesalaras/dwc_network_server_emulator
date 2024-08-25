from .server import TCPServer

class GameStatsServer(TCPServer):
    def __init__(self, ip, port, log_cfg):
        super().__init__(ip, port, log_cfg)
        
        self.db = GSDatabase()
        self.remaining = ""
    async def handle_action(reader, writer):
        """ CONNECTION RECEIVED """
        # Generate a random challenge string (for first time users only)
        self.challenge = rand_str(10, string.ascii_uppercase)
        msg = query.create_message({
            '__cmd__': 'lc',
            '__cmd_val__': '1',
            'challenge': self.challenge,
            'id': '1'
        })
        msg = self.crypt(msg)
        writer.write(msg)
        await writer.drain()
        """ DATA RECEIVED """
        # FIXME: I'm not sure when we'll know we are finished, or when an EOF will be reached...
        data = await reader.read(-1)
        self.remaining += data

        if "\\final\\" not in data:
            return # ? shouldn't this be running forever? jump back to data received?

        # Decrypt full message and reset remaining message
        msg = str(self.crypt(self.remaining))
        self.data = msg
        self.remaining = ""

        commands, self.remaining = query.parse_message(msg)

        # Use function jump table to execute correct command
        for data_parsed in commands:
            print(data_parsed)
        await cmds.get(data_parsed['__cmd__'], cmd_err)(data_parsed, writer)

        # Finally, close the connection
        writer.close()
        await writer.wait_closed()
    async def auth(self, data, writer):
        if 'gamename' in data:
            self.gameid = data['gamename']

        self.session = rand_str(10)

        msg = query.create_message({
            '__cmd__': 'lc',
            '__cmd_val__': '2',
            'sesskey': self.session,
            'proof': 0,
            'id': '1'
        })

        msg = self.crypt(msg)
        writer.write(msg)
        await writer.drain()
    async def auth_parse(self, data, writer):
        parsed_token = utils.parse_authtoken(data['authtoken'], self.db)

        if 'lid' in data:
            self.lid = data['lid']
        uid, pid, gsbrcd, uniquenick = utils.login_profile_via_parsed_token(parsed_token, self.db)
        if pid is not None:
            # Successfully logged in or created account, continue creating session
            sesskey = self.db.create_session(pid, '')
            self.sessions[pid] = self
            self.pid = int(pid)
        pass
    async def ka(self, data, writer):
        pass
    async def setpd(self, data, writer):
        pass
    async def getpd(self, data, writer):
        pass
    async def newgame(self, data, writer):
        return
    async def updgame(self, data, writer):
        return
    def crypt(self, data):
        key = bytearray(b"GameSpy3D")
        key_len = len(key)
        output = bytearray(data.encode("ascii"))

        end = len(output) if not "\\final\\" in output else output.index("\\final\\")

        for i in range(end):
            output[i] ^= key[i % key_len]

        return output

