import datetime as dt
import sqlite3
import json
import time
from flask import Flask, g, render_template, request, jsonify
from contextlib import closing
from math import floor

DATABASE = 'NCAABB.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('NCAAFF_DB_SETTINGS', silent=True)

def connect_db():
    """Returns a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
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


@app.route('/', methods=['GET', 'POST'])
def main():
    """Main start page showing snapshot of standings"""
    yesterday = (dt.date.today() - dt.timedelta(1)).strftime("%Y-%m-%d")
    entries = query_db("""select TeamAway, TeamHome, spread, Predicted FROM Spreads""",
                    one=False)
    results = query_db("""SELECT Team, Opponent, spread, gameDate,
                        Differential,
                        Predicted, beatSpreadSLED
                        FROM PredRes WHERE gameDate=?""",
                        [yesterday])
    return render_template('main.html', entries=entries, results=results)

@app.route('/headtohead', methods=['GET', 'POST'])
def headtohead():
    predictions = g.db.execute("""Select Home, Away, Prediction from Gamematrix""")
    predictionsJson = json.dumps(predictions.fetchall())
    teams = g.db.execute("""SELECT TeamID, teamName FROM Teams""")
    teamsJson = json.dumps(teams.fetchall())
    return render_template('headtohead.html',
                           predictions=predictionsJson,
                           teams=teamsJson)

@app.route('/rankings', methods=['GET', 'POST'])
def rankings():
    entries = query_db("""SELECT Rank, APPoll, CoachesPoll, "SLED.Method" as
            SLEDMethod FROM Rankings""", one =
            False)
    return render_template('rankings.html', entries=entries)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/detailedstats', methods=['GET', 'POST'])
def detailedstats():
    posix = query_db("""SELECT MAX(Calc_Date) AS md FROM SLEDs""")
    posix = posix[0]['md']
#    allconferences = g.db.execute("""SELECT teamName, SLED, conference FROM
#            Conferences, SLEDs WHERE
#            Conferences.TeamID=SLEDs.TeamID AND
#            SLEDs.Calc_Date=? AND SLEDs.method="calc3"
#            ORDER BY SLEDs.SLED DESC""",
#            [posix])
#    return jsonify(dict(('item%d' % i, item)
#                                for i, item in enumerate(allconferences.fetchall(),
#                                    start=1)))
    entries = query_db("""SELECT DISTINCT(Conference) FROM Conferences""",
            one = False)
    return render_template('detailedstats.html', entries=entries)

@app.route('/conference', methods = ['GET', 'POST'])
def conference():
    posix = floor(time.mktime(dt.datetime.now().timetuple())/(60*60*24)) - 1
    conferences = query_db("""SELECT teamName, SLED from Conferences,
        SLEDs WHERE
        Conferences.TeamID = SLEDs.TeamID AND Conference = ?
        AND SLEDs.Calc_Date = ? AND SLEDs.method =
        "calc3" ORDER BY SLEDs.SLED DESC""", [request.form['conference'], posix])
    entries = query_db("""SELECT DISTINCT(Conference) FROM Conferences""", one =
        False)
    return render_template('conference.html', conferences=conferences,
        entries=entries, confname=request.form['conference'])

if __name__ == '__main__':
    app.run()
