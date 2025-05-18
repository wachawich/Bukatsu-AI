import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from flask import request, jsonify, make_response

from collections import defaultdict
import numpy as np
import os
import cv2
import json
import numpy as np

from tqdm import tqdm


def predict_lgbm(user_info, model):
    """
    รับ features เป็น list แล้ว return ผลการพยากรณ์
    """
    le_act = LabelEncoder()
    le_gender = LabelEncoder()
    le_role = LabelEncoder()

    test_rows = []
    
    activity_type = [
        'กิจกรรมอาสา',
        'Open House',
        'กิจกรรมคณะวิศวะ',
        'กิจกรรมคณะวิทย์',
        'อบรม',
        'ประกวด',
        'สัมมนา',
        'สันทนาการ',
        'ชมรม',
        'กิจกรรมวิชาการ',
    ]
    
    gender = [
        'male',
        'female',
        'other'
    ]
    
    role = [
        'นักเรียน',
        'นักศึกษา',
        'บุคลากรทางการศึกษา',
        'ผู้ปกครอง',
        'อื่นๆ'
    ]
    
    le_act.fit(activity_type)
    le_gender.fit(gender)
    le_role.fit(role)

    for act in activity_type:
        row = {
            'activity_type_enc': le_act.transform([act])[0],
            'gender_enc': le_gender.transform([user_info['gender']])[0],
            'role_enc': le_role.transform([user_info['role']])[0],
            'interesting': user_info['interesting'][act],
            'favorite': user_info['favorite'][act],
            'click': user_info['click'][act]
        }
        test_rows.append(row)
    
    X_test = pd.DataFrame(test_rows)
    X_test
    
    scores = model.predict(X_test)

    # แสดงผลลัพธ์เรียงลำดับจากมากไปน้อย
    ranked = sorted(zip(le_act.inverse_transform(X_test['activity_type_enc']), scores), key=lambda x: -x[1])
    for i, (act, score) in enumerate(ranked, 1):
        print(f"{i}. {act} (score: {score:.4f})")
        
    ranked_dict = {i: act for i, (act, score) in enumerate(ranked, 1)}
    
    print(ranked_dict)

    return ranked_dict



def predict_sift_flann(loaded_dataset_features, query_img, sift, flann):
    img_small = cv2.resize(query_img, (0, 0), fx=0.35, fy=0.35)
    query_kp, query_des = sift.detectAndCompute(img_small, None)

    if query_des is None:
        return jsonify({"success": False, "message": "No descriptors found in query image"}), 400

    votes = defaultdict(int)

    for entry in tqdm(loaded_dataset_features):
        # print("entry['des_path']", entry['des_path'])
        des = np.load(f"./model/{entry['des_path']}")
        matches = flann.knnMatch(query_des, des, k=2)

        good = []
        for match in matches:
            if len(match) >= 2:
                m, n = match
                if m.distance < 0.75 * n.distance:
                    good.append(m)

        if len(good) > 10:
            votes[entry['place']] += len(good)

    if votes:
        best_match = max(votes, key=votes.get)
        for entry in loaded_dataset_features:
            if entry['place'] == best_match:
                best_coords = entry['coords']
                break

        if best_coords:
            response = make_response(
                json.dumps({
                    "success": True,
                    "data": best_coords,
                    "message": "Matched place found",
                    "file": entry['des_path']
                }, ensure_ascii=False),
                201
            )
            response.headers["Content-Type"] = "application/json"
            return response

        # สำหรับกรณีที่ไม่พบ match
        else:
            return jsonify({
                "success": False,
                "message": "No good match found"
            }), 404