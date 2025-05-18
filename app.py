from flask import Flask, jsonify, request
import psycopg2
from flask import Flask
from dotenv import load_dotenv
import os
import joblib

# from db.db_connection import get_db_connection
from logic.user import get_user
from logic.process import processFunction
from logic.activity import get_activity, get_activity_ai
from logic.jsonAI import callJsonAPI, updateJsonField
from model.callModel import predict_sift_flann
import numpy as np
from flask_cors import CORS


import cv2

app = Flask(__name__)
CORS(app) 

load_dotenv() 

model = joblib.load('./model/lgb_model.pkl')
import pickle

sift = cv2.SIFT_create()
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

pkl_path = './model/dataset_features.pkl'

with open(pkl_path, 'rb') as f:
    loaded_dataset_features = pickle.load(f)


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


# @app.route("/activity_limit.get.ai", methods=["POST"])
# def getActivityLimitAI():
#     return get_activity_limit_ai(model)

@app.route("/location.predict.ai", methods=["POST"])
def locationPredict():

    if 'image' not in request.files:
            return jsonify({"success": False, "message": "Image file is missing"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

        # อ่านภาพจากไฟล์
    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    query_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    return predict_sift_flann(loaded_dataset_features, query_img, sift, flann)

@app.route('/update_json.ai', methods=['POST'])
def updateJsonAI():
    return updateJsonField()

@app.route("/callJson", methods=["POST"])
def callJsonAI():
    return callJsonAPI()


if __name__ == "__main__":
    app.run(debug=True)
