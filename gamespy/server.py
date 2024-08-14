import asyncio
import logging
import ast
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
    async def handle_action(reader, writer):
        pass
    def crypt(self, data):
        key = bytearray(b"GameSpy3D")
        key_len = len(key)
        output = bytearray(data.encode("ascii"))

        end = len(output) if not "\\final\\" in output else output.index("\\final\\")

        for i in range(end):
            output[i] ^= key[i % key_len]
        pass

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
