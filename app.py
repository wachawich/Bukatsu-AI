from flask import Flask, jsonify
import psycopg2
from flask import Flask
from dotenv import load_dotenv
import os

from db.db_connection import get_db_connection
from logic.user import get_user
from logic.process import processFunction

app = Flask(__name__)

load_dotenv() 

@app.route("/")
def home():
    return jsonify({"message": "Flask API with PostgreSQL"})

# @app.route("/users")
# def get_users():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM users;")
#     rows = cur.fetchall()
#     cur.close()
#     conn.close()
#     return jsonify(rows)

@app.route("/process", methods=["POST"])
def route_get_user():
    return processFunction()

if __name__ == "__main__":
    app.run(debug=True)
