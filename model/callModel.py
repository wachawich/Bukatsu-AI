import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from flask import request, jsonify, make_response
from collections import defaultdict
import os
import cv2
import json
from tqdm import tqdm
from joblib import Parallel, delayed
from functools import partial
from itertools import chain
from multiprocessing import cpu_count
from tqdm.auto import tqdm

def process_single_match(entry, query_des, index_params, search_params):
    # สร้าง FLANN matcher ใหม่สำหรับแต่ละ process
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    des = np.load(f"./model/{entry['des_path']}")
    matches = flann.knnMatch(query_des, des, k=2)
    
    good = []
    for match in matches:
        if len(match) >= 2:
            m, n = match
            if m.distance < 0.75 * n.distance:
                good.append(m)
    
    return entry['place'], len(good) if len(good) > 10 else 0

def process_votes_chunk(chunk):
    votes = defaultdict(int)
    for place, vote_count in chunk:
        if vote_count > 0:
            votes[place] += vote_count
    return dict(votes)

def merge_votes(votes_list):
    final_votes = defaultdict(int)
    for votes in tqdm(votes_list, desc="รวมผลโหวต", leave=False):
        for place, count in votes.items():
            final_votes[place] += count
    return dict(final_votes)

def predict_lgbm(user_info, model):
    """
    รับ features เป็น list แล้ว return ผลการพยากรณ์
    """
    print("เริ่มการทำนายกิจกรรม...")
    le_act = LabelEncoder()
    le_gender = LabelEncoder()
    le_role = LabelEncoder()

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
    
    gender = ['male', 'female', 'other']
    role = ['นักเรียน', 'นักศึกษา', 'บุคลากรทางการศึกษา', 'ผู้ปกครอง', 'อื่นๆ']
    
    print("กำลังเตรียมข้อมูล...")
    with tqdm(total=3, desc="เตรียมข้อมูล") as pbar:
        le_act.fit(activity_type)
        pbar.update(1)
        le_gender.fit(gender)
        pbar.update(1)
        le_role.fit(role)
        pbar.update(1)

    # สร้าง test rows แบบขนาน
    def create_row(act):
        return {
            'activity_type_enc': le_act.transform([act])[0],
            'gender_enc': le_gender.transform([user_info['gender']])[0],
            'role_enc': le_role.transform([user_info['role']])[0],
            'interesting': user_info['interesting'][act],
            'favorite': user_info['favorite'][act],
            'click': user_info['click'][act]
        }

    print("กำลังประมวลผลข้อมูลแบบขนาน...")
    # ใช้ Parallel processing ในการสร้าง rows
    test_rows = Parallel(n_jobs=-1)(
        delayed(create_row)(act) for act in tqdm(activity_type, desc="สร้างข้อมูล", leave=True)
    )
    
    X_test = pd.DataFrame(test_rows)
    print("กำลังทำนายผล...")
    scores = model.predict(X_test)

    # แสดงผลลัพธ์เรียงลำดับจากมากไปน้อย
    ranked = sorted(zip(le_act.inverse_transform(X_test['activity_type_enc']), scores), key=lambda x: -x[1])
    print("\nผลการทำนาย:")
    for i, (act, score) in enumerate(ranked, 1):
        print(f"{i}. {act} (score: {score:.4f})")
        
    ranked_dict = {i: act for i, (act, score) in enumerate(ranked, 1)}
    print("\nสรุปผลการทำนาย:", ranked_dict)

    return ranked_dict

def predict_sift_flann(loaded_dataset_features, query_img, sift, flann):
    print("เริ่มการประมวลผลภาพ...")
    with tqdm(total=2, desc="ประมวลผลภาพ") as pbar:
        img_small = cv2.resize(query_img, (0, 0), fx=0.35, fy=0.35)
        pbar.update(1)
        print("กำลังสกัด features จากภาพ...")
        query_kp, query_des = sift.detectAndCompute(img_small, None)
        pbar.update(1)

    if query_des is None:
        return jsonify({"success": False, "message": "No descriptors found in query image"}), 400

    # สร้าง FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # สร้าง partial function ที่มี parameters ที่จำเป็น
    process_func = partial(process_single_match, 
                         query_des=query_des,
                         index_params=index_params,
                         search_params=search_params)

    print(f"กำลังเปรียบเทียบภาพกับฐานข้อมูล ({len(loaded_dataset_features)} รูป)...")
    # ใช้ Parallel processing ในการเปรียบเทียบภาพ
    results = Parallel(n_jobs=-1)(
        delayed(process_func)(entry) for entry in tqdm(loaded_dataset_features, desc="เปรียบเทียบภาพ", leave=True)
    )

    print("กำลังรวมผลการโหวตแบบขนาน...")
    # แบ่งผลลัพธ์เป็น chunks สำหรับการประมวลผลแบบขนาน
    n_chunks = cpu_count()
    chunk_size = len(results) // n_chunks + (1 if len(results) % n_chunks else 0)
    chunks = [results[i:i + chunk_size] for i in range(0, len(results), chunk_size)]

    # ประมวลผล votes แบบขนาน
    votes_chunks = Parallel(n_jobs=-1)(
        delayed(process_votes_chunk)(chunk) for chunk in tqdm(chunks, desc="ประมวลผลโหวต", leave=True)
    )

    # รวมผลลัพธ์จากทุก chunk
    votes = merge_votes(votes_chunks)

    if votes:
        best_match = max(votes, key=votes.get)
        print(f"\nพบสถานที่ที่ตรงที่สุด: {best_match}")
        for entry in tqdm(loaded_dataset_features, desc="ค้นหาพิกัด", leave=False):
            if entry['place'] == best_match:
                best_coords = entry['coords']
                break

        if best_coords:
            print(f"พิกัด: {best_coords}")
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

    print("\nไม่พบสถานที่ที่ตรงกับภาพ")
    return jsonify({
        "success": False,
        "message": "No good match found"
    }), 404
