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
