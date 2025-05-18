# ตัวอย่าง: ผู้ใช้ใหม่ที่เป็นเพศชาย นักเรียน และ interesting = 1
user_info = {
    'gender': 'male',
    'role': 'นักศึกษา',
    'interesting': {
        "กิจกรรมอาสา" : 0,
        "Open House" : 0,
        "กิจกรรมคณะวิศวะ" : 1,
        "กิจกรรมคณะวิทย์" : 1,
        "อบรม" : 0,
        "ประกวด" : 0,
        "สัมมนา" : 1,
        "สันทนาการ" : 0,
        "ชมรม" : 0,
        "กิจกรรมวิชาการ" : 1,
    },
    'favorite': {
        "กิจกรรมอาสา" : 0,
        "Open House" : 0,
        "กิจกรรมคณะวิศวะ" :47,
        "กิจกรรมคณะวิทย์" : 35,
        "อบรม" : 0,
        "ประกวด" : 0,
        "สัมมนา" : 21,
        "สันทนาการ" : 0,
        "ชมรม" : 0,
        "กิจกรรมวิชาการ" : 12,
    },
    'click': {
        "กิจกรรมอาสา" : 5,
        "Open House" : 2,
        "กิจกรรมคณะวิศวะ" :96,
        "กิจกรรมคณะวิทย์" : 73,
        "อบรม" : 15,
        "ประกวด" : 20,
        "สัมมนา" : 59,
        "สันทนาการ" : 9,
        "ชมรม" : 8,
        "กิจกรรมวิชาการ" : 32,
    }
}

# สร้างข้อมูล test สำหรับทุก activity_type
test_rows = []
for act in df['activity_type'].unique():
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
