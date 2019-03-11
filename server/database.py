"""
Module with SQLite helpers, see http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
"""

import os
import sqlite3
import threading

from flask import g

from server import app


db_filename = os.path.join(os.path.dirname(__file__), 'flags.sqlite')


_init_started = False
_init_lock = threading.RLock()


def _init(database):
    app.logger.info('Creating database schema')
    with app.open_resource('schema.sql', 'r') as f:
        database.executescript(f.read())


def get(context_bound=True):

    global _init_started

    if context_bound and 'database' in g:
        return g.database

    need_init = not os.path.exists(db_filename)
    database = sqlite3.connect(db_filename)
    database.row_factory = sqlite3.Row

    if need_init:
        with _init_lock:
            if not _init_started:
                _init_started = True
                _init(database)

    if context_bound:
        g.database = database
    return database


def query(sql, args=()):
    return get().execute(sql, args).fetchall()


@app.teardown_appcontext
def close(_):
    if 'database' in g:
        g.database.close()
