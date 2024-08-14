from multiprocessing.managers import BaseManager

import sqlite3

class ServerDatabase(BaseManager):
    pass


class GSDatabase:
    def __init__(self, filename='gpcm.db'):
        self.conn = sqlite3.connect(filename, timeout=10.0)
        self.conn.row_factory = sqlite3.Row

    def __del__(self):
        self.close()
    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        
