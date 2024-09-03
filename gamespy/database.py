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
import utils
import json
import time
import string
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
        if self.conn:
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
    def get_next_profileid(self):
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
            profileid = self.get_next_profileid()
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
            password = utils.hash_str(password)

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
        if not self.profile_exists(profileid):
            pid = "11"
            lon = "0.000000"
            lat = "0.000000"

            loc         = ""
            stat        = ""
            partnerid   = ""
            password    = ""
            userid      = ""

            csnum       = ""
            cfc         = ""
            bssid       = ""
            devname     = ""
            birth       = ""
            zipcode     = ""
            aim         = ""

            enabled = 1

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
        return None
    def get_user_list(self):
        with Transaction(self.conn) as tx:
            rows = tx.query("SELECT * FROM users", "all")
        return [self.get_dict(row) for row in rows]
    def save_pending_message(self, sourceid, targetid, msg):
        with Transaction(self.conn) as tx:
            tx.mut_query("INSERT INTO pending_messages VALUES (?,?,?)", (sourceid, targetid, msg))
    def get_pending_messages(self, profileid):
        with Transaction(self.conn) as tx:
            tx.query("SELECT * FROM pending_messages WHERE targetid = ?", (profileid,))
    def update_profile(self, profileid, field):
        if field[0] == "firstname" || field[0] == "lastname":
            with Transaction(self.conn) as tx:
                q = "UPDATE users SET \"%s\" = ? WHERE profileid = ?"
                tx.mut_query(q % field[0], (field[1], profileid))
    # Session functions
    @cache
    def session_to_profileid(self, key):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT profileid FROM sessions WHERE session = ?", (key,), "one")
            r = self.get_dict(row)

        profileid = -1
        if r:
            profileid = r['profileid']
            
        return profileid
    def loginticket_to_profileid(self, loginticket):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT profileid FROM sessions WHERE loginticket = ?", (loginticket,))

        profileid = -1
        if row:
            profileid = int(row[0])

        return profileid
    def session_to_profile(self, key):
        profileid = self.session_to_profileid(key)

        profile = {}
        if profileid:
            with Transaction
    def generate_key(self, min_size):
        session_key = utils.register_rand(min_size, string.digits)
        return session_key
    def delete_session(self, profileid):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT session FROM sessions WHERE profileid = ?", (profileid,), "one")
        if row:
            utils.deregister_rand(str(row[0]))
        with Transaction(self.conn) as tx:
            tx.mut_query("DELETE FROM sessions WHERE profileid = ?", (profileid,))
    def create_session(self, profileid, loginticket):
        if not profileid and not self.profile_exists(profileid):
            return None
        self.delete_session(profileid)
        session_key = self.generate_key(8)
        with Transaction(self.conn) as tx:
            tx.mut_query("INSERT INTO sessions VALUES (?, ?, ?)", (session_key, profileid, loginticket))
        return session_key
    def session_list(self, profileid=None):
        with Transaction(self.conn) as tx:
            if profileid:
                rows = tx.query("SELECT * FROM sessions WHERE profileid = ?", (profileid,), "one")
            else:
                rows = tx.query("SELECT * FROM sessions", type="all")
        return [self.get_dict(row) for row in rows]
    # NAS Server
    def get_nas_login(self, authtoken):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT data FROM nas_logins WHERE authtoken = ?", (authtoken,), "one")
            r = self.get_dict(row)

        if not r:
            return None
        else:
            return json.loads(r['data'])
    def userid_to_nas_login(self, userid):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT data FROM nas_logins WHERE userid = ?", (userid,), "one")
            r = self.get_dict(row)

        if not r:
            return None
        else:
            return json.loads(r['data'])
    def is_banned(self, postdata):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT COUNT(*) FROM banned WHERE gameid = ? AND ipaddr = ?", (postdata['gamecd'][:-1], postdata['ipaddr']), "one")
        return int(row[0]) > 0
    def is_pending(self, postdata):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT COUNT(*) FROM registered WHERE macaddr = ?", (postdata['macaddr'],), "one")
        return int(row[0]) > 0
    def is_registered(self, postdata):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT COUNT(*) FROM registered WHERE macaddr = ?", (postdata['macaddr'],), "one")
        return int(row[0]) > 0
    def get_next_userid(self):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT max(userid) as maxuser FROM users", type="one")
            r = self.get_dict(row)
        if not r or r['maxuser'] is None:
            # Because all zeroes means Dolphin. Don't wanna get confused
            # during debugging later.
            return '0000000000002'
        else:
            userid = int(r['maxuser']) + 1
            userid = f'{userid:013}'
            
    def generate_authtoken(self, userid, data):
        size = 80
        authtoken = "NDS" + utils.register_rand(size)

        with Transaction(self.conn) as tx:
            row = tx.query("SELECT * FROM nas_logins WHERE userid = ?", (userid,))
            r = self.get_dict(row)
        if "devname" in data:
            data["devname"] = utils.encode(data["devname"], type="b64")
        if "ingamesn" in data:
            data["ingamesn"] = utils.encode(data["ingamesn"], type="b64")
        data = json.dumps(data)

        with Transaction(self.conn) as tx:
            if not r:
                tx.mut_query("INSERT INTO nas_logins VALUES (?, ?, ?)", (userid, authtoken, data))
            else:
                tx.mut_query("UPDATE nas_logins SET authtoken = ?, data = ? WHERE userid = ?", (authtoken, data, userid))
        return authtoken
    # Buddy functions
    def add_buddy(self, userProfileId, buddyProfileId):
        now = int(time.time())

        with Transaction(self.conn) as tx:
            tx.mut_query("INSERT INTO buddies VALUES (?, ?, ?, ?, ?, ?, ?)", 
                         (1, userProfileId, buddyProfileId)
            )
    def auth_buddy(self, userProfileId, buddyProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("UPDATE buddies SET status = ? WHERE userProfileId = ? AND buddyProfileId = ?", (1, userProfileId, buddyProfileId))
    def block_buddy(self, userProfileId, buddyProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("UPDATE  buddies SET blocked = ? WHERE userProfileId = ? AND buddyProfileId = ?", (1, userProfileId, buddyProfileId))
    def unblock_buddy(self, userProfileId, buddyProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("UPDATE buddies SET blocked = ? WHERE userProfileId = ? AND buddyProfileId = ?", (0, userProfileId, buddyProfileId))
    def get_buddy(self, userProfileId, buddyProfileId):
        if userProfileId and buddyProfileId:
            with Transaction(self.conn) as tx:
                tx.query("SELECT * FROM buddies WHERE userProfileId = ? AND buddyProfileId = ?", (userProfileId, buddyProfileId), "one")
            return self.get_dict(row)
        return {}
    def delete_buddy(self, userProfileId, buddyProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("DELETE FROM buddies WHERE userProfileId = ? AND buddyProfileId = ?", (userProfileId, buddyProfileId))
    def buddy_list(self, userProfileId):
        with Transaction(self.conn) as tx:
            rows = tx.query("SELECT * FROM buddies WHERE userProfileId = ? AND blocked = 0", (userProfileId,), "all")
        return [self.get_dict(row) for row in rows]
    def blocked_list(self, userProfileId):
        with Transaction(self.conn) as tx:
            rows = tx.query("SELECT * FROM buddies WHERE userPorfileId = ? AND blocked = 1", (userProfileId,), "all")
        return [self.get_didct(row) for row in rows]
    def pending_buddy_requests(self, userProfileId):
        with Transaction(self.conn) as tx:
            rows = tx.query("SELECT * FROM buddies WHERE buddyProfileId = ? AND status = 1 AND notified = 0", (userProfileId), "all")
        return [self.get_dict(row) for row in rows]
    def buddy_need_auth_message(self, userProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("UPDATE buddies SET notified = ? WHERE userProfileId = ? AND buddyProfileId = ?", (1, userProfileId, buddyProfileId))
        return [self.get_dict(row) for row in rows]
    def buddy_sent_auth_message(self, userProfileId):
        with Transaction(self.conn) as tx:
            tx.mut_query("UPDATE buddies SET notified = ? WHERE userProfileId = ? AND buddyProfileId = ?", (1, userProfileId, buddyProfileId))
    # Gamestats related functions
    def pd_insert(self, profileid, dindex, ptype, data):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT COUNT(*) FROM gamestat_profile WHERE profileid = ? AND dindex = ? AND ptype = ?", (profileid, dindex, ptype))
            count = int(row[0])
            if count > 0:
                tx.mut_query("UPDATE gamestat_profile SET data = ? WHERE profileid = ? AND dindex = ? AND ptype = ?", (data, profileid, dindex, ptype))
            else:
                tx.mut_query("INSERT INTO gamestat_profile (profileid, dindex, ptype, data) VALUES(?, ?, ?, ?)", (profileid, dindex, ptype, data))
    def pd_get(self, profileid, dindex, ptype):
        with Transaction(self.conn) as tx:
            row = tx.query("SELECT * FROM gamestat_profile WHERE profileid = ? AND dindex = ? AND ptype = ?", (profileid, dindex, ptype))
        return self.get_dict(row)        
