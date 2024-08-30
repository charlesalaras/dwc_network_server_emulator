CREATE TABLE IF NOT EXISTS users (
    profileid      INT,
    userid         TEXT,
    password       TEXT,
    gsbrcd         TEXT,
    email          TEXT,
    uniquenick     TEXT,
    pid            TEXT,
    lon            TEXT,
    lat            TEXT,
    loc            TEXT,
    firstname      TEXT,
    lastname       TEXT,
    stat           TEXT,
    partnerid      TEXT,
    console        INT,
    csnum          TEXT,
    cfc            TEXT,
    bssid          TEXT,
    devname        BLOB,
    birth          TEXT,
    gameid         TEXT,
    enabled        INT,
    zipcode        TEXT,
    aim            TEXT
)

CREATE TABLE IF NOT EXISTS sessions (
    session        TEXT,
    profileid      INT,
    loginticket    TEXT
)

CREATE TABLE IF NOT EXISTS buddies (
    userProfileId  INT,
    buddyProfileId INT,
    time           INT,
    status         INT,
    notified       INT,
    gameid         TEXT,
    blocked        INT
)

CREATE TABLE IF NOT EXISTS pending_messages (
    sourceid       INT,
    targetid       INT,
    gameid         TEXT
)

CREATE TABLE IF NOT EXISTS gamestat_profile (
    profileid      INT,
    targetid       INT
)

CREATE TABLE IF NOT EXISTS gameinfo (
    profileid      INT,
    dindex         TEXT,
    ptype          TEXT,
    data           TEXT
)

CREATE TABLE IF NOT EXISTS nas_logins (
    userid         TEXT,
    authtoken      TEXT,
    data           TEXT
)

CREATE TABLE IF NOT EXISTS banned (
    gameid         TEXT,
    ipaddr         TEXT
)

CREATE TABLE IF NOT EXISTS pending     (macaddr TEXT)
CREATE TABLE IF NOT EXISTS registered  (maxaddr TEXT)

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS gamestatprofile_triple         ON gamestat_profile (profileid, dindex, ptype)
CREATE UNIQUE INDEX IF NOT EXISTS user_profileid_idx             ON users (profileid)
CREATE INDEX IF NOT EXISTS        user_userid_idx                ON users (userid)
CREATE INDEX IF NOT EXISTS        pending_messages_targetid_idx  ON pending_messages (targetid)
CREATE UNIQUE INDEX IF NOT EXISTS sessions_session_idx           ON sessions (session)
CREATE INDEX IF NOT EXISTS        sessions_loginticket_idx       ON sessions (loginticket)
CREATE INDEX IF NOT EXISTS        sessions_profileid_idx         ON sessions (profileid)
CREATE UNIQUE INDEX IF NOT EXISTS nas_logins_authtoken_idx       ON nas_logins (authtoken)
CREATE INDEX IF NOT EXISTS        nas_logins_userid_idx          ON nas_logins (userid)
CREATE INDEX IF NOT EXISTS        buddies_userProfileId_idx      ON buddies (userProfileId)
CREATE INDEX IF NOT EXISTS        buddies_buddyProfileId_idx     ON buddies (buddyProfileId)
CREATE INDEX IF NOT EXISTS        gamestat_profile_profileid_idx ON gamestat_profile (profileid)
