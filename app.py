from flask import Flask
import psycopg2
import os

url = os.environ.get("DATABASE_URL")
db_conn = psycopg2.connect(url)
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/dbtest")
def dbtest():
    query = 'SELECT VERSION()'
    with db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute(query)
            version = cursor.fetchone()[0]
        return {"version": version}, 201