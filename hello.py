import sqlite3
from contextlib import closing
from flask import Flask, render_template, request, session, url_for, \
    abort, flash, g, redirect


#CONFIG
DATABASE = '/tmp/hello.db'
DEBUG=True
SECRET_KEY = 'develop key'
USERNAME = 'qd'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('shema.sql', mode = 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    if exception is not None:
        app.logger.error(exception)

@app.route('/')
def hello():
    cur = g.db.execute('select title, text from entries order by id desc;')
    entries = [dict(title = row[0], text = row[1]) for row in cur.fetchall()]
    return render_template('hello.html', entries = entries)

@app.route('/add', methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    app.logger.info('post %s added successfully' % request.form['title'])
    return redirect(url_for('hello'))

@app.route('/users/<username>')
def show_user_profile(username):
    # show the user profile page
    return 'user <b>%s</b>' % username

@app.route('/about')
def about():
    # show the user profile page
    return 'The about page<br>author: Yegor D.'

@app.route('/projects/')
def projects():
    # show the user profile page
    return 'The project page'

def valid_login(username, password):
    return (app.config['USERNAME'] == username and
           app.config['PASSWORD'] == password )

def do_login(username):
    session['logged_in'] = True
    flash('You where logged in!')
    return redirect(url_for('hello'))

@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return do_login(request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You where logged out!')
    return redirect(url_for('hello'))

if __name__ == "__main__":
    app.run()
