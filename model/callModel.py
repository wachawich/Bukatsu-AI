import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder

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
