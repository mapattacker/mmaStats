from bs4 import BeautifulSoup
import urllib, sqlite3, time, traceback

######### CREATE SQLITE TABLE ############
conn = sqlite3.connect('MMA.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS fighter;
DROP TABLE IF EXISTS relation;
DROP TABLE IF EXISTS html;
DROP TABLE IF EXISTS nationality;
DROP TABLE IF EXISTS weightClass;

CREATE TABLE fighter (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    url             TEXT UNIQUE,
    scanned         TEXT,
    name            TEXT,
    count_new       INTEGER,
    birthday        TEXT,
    weightClass_id  INTEGER,
    country_id      INTEGER,
    First_Fight     TEXT,
    Last_Fight      TEXT,
    totalFights     INTEGER,
    totalWins       INTEGER,
    totalLosses     INTEGER,
    totalDraws      INTEGER,
    totalNC         INTEGER
);

CREATE TABLE relation (
    from_id          INTEGER,
    to_id            INTEGER
);

CREATE TABLE nationality (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    country         TEXT UNIQUE
);

CREATE TABLE weightClass (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    weight          TEXT UNIQUE
)
''')

print 'Database and tables Created'
