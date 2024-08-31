"""DWC Network Server Emulator

    Copyright (C) 2014 polaris-
    Copyright (C) 2014 ToadKing
    Copyright (C) 2014 AdmiralCurtiss
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

from multiprocessing.managers import BaseManager

import sqlite3
import os
from hashlib import pbkdf2_hmac

class ServerDatabase(BaseManager):
    pass

class Transaction:
    def __init__(self, connection):
        self.conn = connection
        self.altered = False
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        if self.altered:
            self.conn.commit()
        return
    def _measure_exec(self, cursor, statement, params):
        pass
    def query(self, statement, params=(), type="all"):
        """
        Runs a given SQL statement, expecting database to remain unchanged

        Parameters
        ----------
        statement : str
            The SQL statement to be executed, must be sanitized
        params : tuple
            Parameters to the SQL statement
        type : str, "all" or "one"
            Determines whether to return one row or all matching rows

        Returns
        -------
        dict, representing the row data

        Raises
        ------
        ValueError
            If type ("all" or "one") is not a valid string option.
        """
        data = None
        with closing(self.conn.cursor()) as cursor:
            self._measure_exec(cursor, statement, params)
            if type == "all":
                data = cursor.fetchall()
            else if type == "one":
                data = cursor.fetchone()
            else:
                raise ValueError(f"Invalid 'type' received: {type}")
        return data
    def mut_query(self, statement, params=()):
        """
        Runs a given SQL statement, altering the database

        Parameters
        ----------
        statement : str
            The SQL statement to be executed, must be sanitized
        params : tuple
            Parameters to the SQL statement

        Returns
        -------
        int, representing the row id
        """
        rowid = None
        with closing(self.conn.cursor()) as cursor:
            self._measure_exec(cursor, statement, params)
            # This works fine for single row updates, which we usually expect from a cursor.
            # FIXME: Does this actually ignore other cursors?
            rowid = cursor.lastrowid()
            self.altered = True
            
        return rowid
        

class GSDatabase:
    def __init__(self, filename='gpcm.db'):
        self.conn = sqlite3.connect(filename, timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        # FIXME: This *may* be different for each database instance...
        self.salt = os.urandom(16)

    def __del__(self):
        self.close()
    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        pass
    def init_db(self):
        with open('schema.sql', 'r') as f:
            schema = f.read()
        with closing(self.conn.cursor()) as cursor:
            cursor.executescript(schema)
    def get_dict(self, row):
        return None if not row else dict(zip(row.keys(), row))
    # User functions
    def get_next_free_profileid(self):
        """
        TODO: profileid must be 1 at start of game
        """
        with Transaction(self.conn) as tx:
            row_id = tx.mut_query("INSERT INTO users DEFAULT VALUES")
            row_data = tx.query("SELECT profileid AS m FROM users WHERE rowid = ?", (row_id))

        profileid = 1
        if row_data is not None and row_data['m'] is not None:
            profileid = int(r['m']) + 1
        return profileid
    def user_exists(self, userid, gsbrcd):
        with Transaction(self.conn) as tx:
            row_data = tx.query("SELECT COUNT(*) FROM users WHERE userid = ? AND gsbrcd = ?",
                                (userid, gsbrcd), "one")
            count = int(row[0])
        return count > 0
    def user_enabled(self, userid, gsbrcd):
        with Transaction(self.conn) as tx:
            row_data = tx.query("SELECT enabled FROM users WHERE userid = ? AND gsbrcd = ?",
                                (userid, gsbrcd), "one")
            enabled = int(row[0])
        return enabled > 0
    def profile_exists(self, profileid):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT COUNT(*) FROM users WHERE profileid = ?",
                           (profileid,), "one")
            count = int(row[0])
        return count > 0
    def get_profile(self, profileid):
        profile = {}
        if profileid:
            with Transaction(self.conn) as tx:
                row = tx.query("SELECT * FROM users WHERE profileid = ?", (profileid,))
                profile = self.get_dict(row)
            return profile
        else:
            raise ValueError("Invalid profileid: {}", profileid)
    def new_user(self, 
                 userid, 
                 password, 
                 email, 
                 uniquenick, 
                 gsbrcd, 
                 console, 
                 csnum, 
                 cfc, 
                 bssid, 
                 devname, 
                 birth, 
                 gameid, 
                 macaddr):
        if not self.user_exists(userid, gsbrcd):
            profileid = self.get_next_free_profileid()
            # Unknown why the following values must be this
            pid = "11" 
            lon = "0.000000"
            lat = "0.000000"

            loc       = ""
            firstname = ""
            lastname  = ""
            stat      = ""
            partnerid = ""
            enabled   = 1
            zipcode   = ""
            aim       = ""
            # Iterations are low since security is not too big of a concern here?
            # NOTE: If you're erroring out here, your Python 3.12+ wasn't compiled with OpenSSL.
            dk = pbkdf2_hmac('sha256', password.encode(), self.salt, 100_000)
            password = dk.hex()

            # Ugly code incoming
            with Transaction(self.conn) as tx:
                q = "INSERT INTO users VALUES " \
                    "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                tx.mut_query(q, (profileid, 
                             str(userid), 
                             password, 
                             gsbrcd, 
                             email, 
                             uniquenick, 
                             pid, 
                             lon, 
                             lat, 
                             loc, 
                             firstname, 
                             lastname, 
                             stat, 
                             partnerid, 
                             console, 
                             csnum, 
                             cfc, 
                             bssid, 
                             devname, 
                             birth, 
                             gameid, 
                             enabled, 
                             zipcode, 
                             aim))
                
            return profileid
        return None # user exists, maybe raise an error here?
    def import_user(self, profileid, uniquenick, firstname, lastname, email, gsbrcd, gameid, console):
        pass
    @cache
    def session_key_to_profileid(self, key):
        
