"""DWC Network Server Emulator

    Copyright (C) 2014 polaris-
    Copyright (C) 2014 ToadKing
    Copyright (C) 2014 AdmiralCurtiss
    Copyright (C) 2014 msoucy
    Copyright (C) 2015 Sepalani
    Copyright (C) 2024 Charles Alaras

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import asyncio
import logging
import string
import ast

import query
from database import GSDatabase
from enum import Enum

# Begin TCP Servers!

class TCPServer:
    def __init__(self, ip="0.0.0.0", port=29920, log_cfg={ LoggerName: "UnknownTCPServer", LoggerFilename: "unkown_tcp_server.log", LoggerLevel: -1, LoggerOutputConsole: True, LoggerOutputFile: True}):
        self.ip = ip
        self.port = port
        self.logger = create_logger(log_cfg)
    async def handle_action(reader, writer):
        # If someone connects to our server, send a challenge

        # If we receive data from someone, parse it into a GameSpy message
        pass
    async def start(self):
        self.server = await asyncio.start_server(self.handle_action, self.ip, self.port)

        async with self.server:
            await self.server.serve_forever()
        pass

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

class PlayerSearchServer(TCPServer):
    def __init__(address):
        super.__init__()

        self.db = "FIXME: DB GOES HERE"
        self.address = address
        self.remaining = ""
    async def handle_action(reader, writer):
        data = await reader.read(-1)

        data = self.remaining + data
        message, self.remaining = query.parse_message(data)

        if message['__cmd__'] == 'otherslist':
            self.otherslist(message, writer)
        else:
            throw RuntimeError("Could not parse command!")
                
        pass
    def otherslist(self, data_parsed, writer):
        # "The client sends a list with profile ids to the server to translate them into user nicks"

        # "The server answers with a sequence of o+uniquenick pairs; one pair for each requested id of opids." Sort by profile ids of the parameter o. "Parameter oldone" terminates the sequence
        res = {
            '__cmd__': 'otherslist',
            '__cmd_val__': '',
        }

        if 'numopids' in data_parsed and 'opids' in data_parsed:
            numopids = int(data_parsed['numopids'])
            opids = data_parsed['opids'].split('|')

        res['oldone'] = ""
        res = query.create_message(res)

        otherslist
    
# Begin UDP Servers!

# Not necessarily a "server"...
class TokenType(Enum):
    UNKNOWN = 0
    FIELD = 1
    STRING = 2
    NUMBER = 3
    TOKEN = 4
class BackendServer:
    def __init__(self):
        self.server_list = {}
        self.natneg_list = {}
    def get_token(self, filters):
        i = 0
        start = 0
        token_type = TokenType.UNKNOWN
        while i < len(filters) and filters[i].isspace():
            i += 1
            start += 1
        while i < len(filters):
            match filters[i]:
                case ' ':
                    i += 1
                    start += 1
                case '(' | ')' | '&' | '=':
                    i += 1
                    token_type = TokenType.TOKEN
                case '>' | '<':
                    i += 1
                    token_type = TokenType.TOKEN
                    i += int(i < len(filters) and filters[i] == '=')
                case '\'' | '\"':
                    delimiter = '\'' if filters[i] == '\'' else '\"'
                    token_type = TokenType.STRING

                    i += 1
                    while i < len(filters) and filters[i] != delimiter:
                        i += 1
                    if i < len(filters) and filters[i] == delimiter:
                        i += 1
                case _:
                    # FIXME: Do lots of final checks here
                    i += 1
        token = filters[start:i]
        token = token.lower() if token_type == TokenType.FIELD and (token.lower() == "and" or token.lower() == "or") else token
        return token, i, token_type
    def validate_ast(self, node, num_literal_only, is_sql=False):
        valid_node = False
        match node:
            case ast.Num:
                valid_node = True
            case ast.Str:
                if is_sql or not num_literal_only:
                    valid_node = True
            case ast.BoolOp:
                for value in node.values:
                    valid_node = self.validate_ast(value, num_literal_only)
                if not valid_node:
                    break
            case ast.BinOp:
                is_sql |= \
                    hasattr(node, "left") and \
                    hasattr(node.left, "right") and \
                    isinstance(node.left.right, ast.Name) and \
                    node.left.right.id in sql_commands
                valid_node = self.validate_ast(node.left, True, is_sql)
                if valid_node:
                    valid_node = self.validate_ast(node.right, True, is_sql)
            case ast.UnaryOp:
                valid_node = self.validate_ast(node.operand, num_literal_only)
            case ast.Expr:
                valid_node = self.validate_ast(node.value, num_literal_only)
            case ast.Compare:
                valid_node = self.validate_ast(node.left, num_literal_only)

                for op in node.ops:
                    if isinstance(op, ast.Is) or isinstance(op, ast.IsNot) or isinstance(op, ast.In) or isinstance(op, ast.NotIn):
                        valid_node = False
                        break
                if valid_node:
                    for expr in node.comparators:
                        valid_node = self.validate_ast(expr, num_literal_only)
            case ast.Call:
                valid_node = False
            case ast.Name:
                valid_node = node.id in sql_commands
            case _:
                valid_node = False
        return valid_node
