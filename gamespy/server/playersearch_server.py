from .server import TCPServer

class PlayerSearchServer(TCPServer):
    def __init__(address):
        super.__init__()

        self.db = "FIXME: DB GOES HERE"
        self.address = address
        self.remaining = ""
    async def handle_action(reader, writer):
        data = await reader.read(-1)

        data = self.remaining + data
        message, remaining = query.parse_message(data)
        self.remaining += remaining

        if message['__cmd__'] == 'otherslist':
            self.otherslist(message, writer)
        #else:
        #    throw RuntimeError("Could not parse command!")
        # Wait for message to complete first
        pass
    async def otherslist(self, data_parsed, writer):
        # "The client sends a list with profile ids to the server to translate them into user nicks"

        # "The server answers with a sequence of o+uniquenick pairs; one pair for each requested id of opids." Sort by profile ids of the parameter o. "Parameter oldone" terminates the sequence
        res = {
            '__cmd__': 'otherslist',
            '__cmd_val__': '',
        }
        # Note: check that these exist
        if "numopids" in data_parsed.keys() and "opids" in data_parsed.keys():
            numopids = int(data_parsed['numopids'])
            opids = data_parsed['opids'].split('|')
        # Error out if numopids doesn't match, realistically is never checked though...
        else:
            raise ValueError("OPIDs not found in list")
        res['o'] = []
        res['uniquenick'] = []
        for profileid in opids:
            profile = self.db.get_profile(profileid)
            res['o'].append(opid)
            if profile is not None:
                res['uniquenick'].append(profile['uniquenick'])
            else:
                res['uniquenick'].append('')

        res['oldone'].append("")
        msg = query.create_message(res)

        writer.write(msg)
        await writer.drain()
 
