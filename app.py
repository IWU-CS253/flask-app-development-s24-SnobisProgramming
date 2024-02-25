# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    # Fetch all categories to use in the dropdown and assign it to a variable.
    cur = db.execute('SELECT DISTINCT category FROM entries')
    categories = [row[0] for row in cur.fetchall()]
    category = request.args.get('category')
    # This if/else determines category filtering.
    if category:
        cur = db.execute('SELECT title, text, category FROM entries WHERE category = ? ORDER BY id DESC', [category])
        entries = cur.fetchall()
    else:
        cur = db.execute('SELECT title, text, category FROM entries ORDER BY id DESC')
        entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, category=category, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('INSERT INTO entries (title, text, category) VALUES (?, ?, ?)',
               [request.form['title'], request.form['text'], request.form['category']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


# This reroutes back to the main page with the selected category to filter by
@app.route('/filter', methods=['POST'])
def filter_entries():
    category = request.form['category']
    return redirect(url_for('show_entries', category=category))


# Out of ideas for what is wrong. I'm unsure why this doesn't actually delete the entry.
@app.route('/delete', methods=['POST'])
def delete_entry():
    db = get_db()
    entry_id = request.form['entry_id']
    # Shouldn't this be the correct way to delete an entry?
    db.execute('DELETE FROM entries WHERE id = ?', [entry_id])
    db.commit()
    flash('Wow. You just deleted that entry.')
    return redirect(url_for('show_entries'))
