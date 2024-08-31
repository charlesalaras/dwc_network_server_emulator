-- Should all these be text?
CREATE TABLE IF NOT EXISTS users (
    profileid      INT, -- No default because autoincrement?
    userid         TEXT DEFAULT (""),
    password       TEXT DEFAULT (""),
    gsbrcd         TEXT DEFAULT (""),
    email          TEXT DEFAULT (""),
    uniquenick     TEXT DEFAULT (""),
    pid            TEXT DEFAULT (""),
    lon            TEXT DEFAULT (""),
    lat            TEXT DEFAULT (""),
    loc            TEXT DEFAULT (""),
    firstname      TEXT DEFAULT (""),
    lastname       TEXT DEFAULT (""),
    stat           TEXT DEFAULT (""),
    partnerid      TEXT DEFAULT (""),
    console        INT  DEFAULT 1,
    csnum          TEXT DEFAULT (""),
    cfc            TEXT DEFAULT (""),
    bssid          TEXT DEFAULT (""),
    devname        BLOB, -- Default Value?
    birth          TEXT DEFAULT (""),
    gameid         TEXT DEFAULT (""),
    enabled        INT  DEFAULT 0,
    zipcode        TEXT DEFAULT (""),
    aim            TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS sessions (
    session        TEXT DEFAULT (""),
    profileid      INT  DEFAULT 1,
    loginticket    TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS buddies (
    userProfileId  INT  DEFAULT 1,
    buddyProfileId INT  DEFAULT 1,
    time           INT  DEFAULT 0,
    status         INT  DEFAULT 0,
    notified       INT  DEFAULT 0,
    gameid         TEXT DEFAULT (""),
    blocked        INT  DEFAULT 0
)

CREATE TABLE IF NOT EXISTS pending_messages (
    sourceid       INT  DEFAULT 0,
    targetid       INT  DEFAULT 0,
    gameid         TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS gamestat_profile (
    profileid      INT  DEFAULT 1,
    targetid       INT  DEFAULT 0
)

CREATE TABLE IF NOT EXISTS gameinfo (
    profileid      INT  DEFAULT 1,
    dindex         TEXT DEFAULT (""),
    ptype          TEXT DEFAULT (""),
    data           TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS nas_logins (
    userid         TEXT DEFAULT (""),
    authtoken      TEXT DEFAULT (""),
    data           TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS banned (
    gameid         TEXT DEFAULT (""),
    ipaddr         TEXT DEFAULT ("")
)

CREATE TABLE IF NOT EXISTS pending     (macaddr TEXT DEFAULT (""))
CREATE TABLE IF NOT EXISTS registered  (macaddr TEXT DEFAULT (""))

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS gamestatprofile_triple         ON gamestat_profile (profileid, dindex, ptype)
CREATE UNIQUE INDEX IF NOT EXISTS user_profileid_idx             ON users            (profileid)
CREATE INDEX IF NOT EXISTS        user_userid_idx                ON users            (userid)
CREATE INDEX IF NOT EXISTS        pending_messages_targetid_idx  ON pending_messages (targetid)
CREATE UNIQUE INDEX IF NOT EXISTS sessions_session_idx           ON sessions         (session)
CREATE INDEX IF NOT EXISTS        sessions_loginticket_idx       ON sessions         (loginticket)
CREATE INDEX IF NOT EXISTS        sessions_profileid_idx         ON sessions         (profileid)
CREATE UNIQUE INDEX IF NOT EXISTS nas_logins_authtoken_idx       ON nas_logins       (authtoken)
CREATE INDEX IF NOT EXISTS        nas_logins_userid_idx          ON nas_logins       (userid)
CREATE INDEX IF NOT EXISTS        buddies_userProfileId_idx      ON buddies          (userProfileId)
CREATE INDEX IF NOT EXISTS        buddies_buddyProfileId_idx     ON buddies          (buddyProfileId)
CREATE INDEX IF NOT EXISTS        gamestat_profile_profileid_idx ON gamestat_profile (profileid)
