from flask import Flask, jsonify
import psycopg2
from flask import Flask
from dotenv import load_dotenv
import os
import joblib

# from db.db_connection import get_db_connection
from logic.user import get_user
from logic.process import processFunction
from logic.activity import get_activity, get_activity_ai
from logic.jsonAI import callJsonAPI

app = Flask(__name__)

load_dotenv() 

model = joblib.load('./model/lgb_model.pkl')

@app.route("/")
def home():
    return jsonify({"message": "Flask API with PostgreSQL"})

@app.route("/process", methods=["POST"])
def processUserInfoJson():
    return processFunction(model)

@app.route("/activity.get", methods=["POST"])
def getActivity():
    return get_activity()

@app.route("/activity.get.ai", methods=["POST"])
def getActivityAI():
    return get_activity_ai(model)

@app.route("/callJson", methods=["POST"])
def callJsonAI():
    return callJsonAPI()

if __name__ == "__main__":
    app.run(debug=True)
