import sqlite3
from flask import Flask, g, render_template, request
from contextlib import closing

DATABASE = 'NCAABB.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('NCAAFF_DB_SETTINGS', silent = True)

def connect_db():
    """Returns a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one = False):
    """Queries the database and returns a list of dictionaries"""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods = ['GET', 'POST'])
def start():
    """Main start page showing snapshot of standings"""
    entries = query_db("""select Team_Away, Team_Home, spread FROM Spreads""",
                    one = False)
    results = query_db("""SELECT Team_Away, Team_Home, spread, LIRApred,
                        SLEDpred, spreadLIRAdiff, spreadWin,
                        LIRAWin, SLEDWin, beatSpread,
                        beatSpread2, beatSpreadSLED, beatSpreadSLED2
                        FROM PredRes""")
    return render_template('main.html', entries = entries, results=results)

@app.route('/headtohead', methods = ['GET', 'POST'])
def headtohead():
    homeentries = query_db("""Select Team_Name, Team_ID from Lookup ORDER BY
                            Team_Name ASC""", one = False)
    awayentries = query_db("""Select Team_Name, Team_ID from Lookup ORDER BY
                            Team_Name ASC""", one = False)
    return render_template('headtohead.html', homeentries = homeentries,
            awayentries = awayentries)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    entries = query_db("""SELECT Home, Away, Prediction
            FROM Gamematrix WHERE
            Home = ? AND Away = ?""",
            [request.form['home'], request.form['away']])
    away = query_db("""SELECT Team_Name FROM Lookup where Team_ID = ?""",
            [request.form['away']])
    home = query_db("""SELECT Team_Name FROM Lookup where Team_ID = ?""",
            [request.form['home']])
    return render_template('results.html', entries = entries, home=home,
            away=away)

if __name__ == '__main__':
    app.run()