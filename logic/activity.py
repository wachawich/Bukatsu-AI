from flask import request, jsonify
from db.db_connection import get_db_connection, get_db_connection_AI

from logic.jsonAI import callJson
from model.callModel import predict_lgbm

def get_activity():
    data = request.get_json()

    keys = [
        "activity_id", "title", "create_date", "start_date", "end_date",
        "status", "create_by", "location_id", "location_name", "location_type", "flag_valid"
    ]

    if not any(data.get(k) for k in keys):
        return jsonify({ "success": False, "message": "No value input!" }), 404

    query = """
    SELECT * FROM activity a
    LEFT JOIN location l ON l.location_id = a.location_id
    WHERE a.activity_id > 0
    """

    for key in keys:
        value = data.get(key)
        if value is not None:
            if isinstance(value, str):
                query += f" AND {alias_prefix(key)}.{key} = '{value}' \n"
            else:
                query += f" AND {alias_prefix(key)}.{key} = {value} \n"

    print(query)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ดึง activity หลัก
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        if not rows:
            cur.close()
            conn.close()
            return jsonify({ "success": True, "data": [] }), 200

        activity_id = rows[0]['activity_id']

        # ดึง activity_type_normalize
        query_type = f"""
        SELECT * FROM public.activity_type_normalize atn
        LEFT JOIN activity_type at ON at.activity_type_id = atn.activity_type_id
        WHERE atn.activity_id = {activity_id}
        """
        cur.execute(query_type)
        type_columns = [desc[0] for desc in cur.description]
        type_data = [dict(zip(type_columns, row)) for row in cur.fetchall()]

        # ดึง activity_subject_normalize
        query_subject = f"""
        SELECT * FROM public.activity_subject_normalize asn
        LEFT JOIN subject s ON s.subject_id = asn.subject_id
        WHERE asn.activity_id = {activity_id}
        """
        cur.execute(query_subject)
        subject_columns = [desc[0] for desc in cur.description]
        subject_data = [dict(zip(subject_columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()

        # จัดกลุ่มข้อมูล
        ac_type_grouped = {}
        for row in type_data:
            aid = row['activity_id']
            ac_type_grouped.setdefault(aid, []).append(row)

        sub_type_grouped = {}
        for row in subject_data:
            aid = row['activity_id']
            sub_type_grouped.setdefault(aid, []).append(row)

        enriched_data = []
        for activity in rows:
            aid = activity['activity_id']
            enriched_data.append({
                **activity,
                "activity_type_data": ac_type_grouped.get(aid, []),
                "activity_subject_data": sub_type_grouped.get(aid, [])
            })

        return jsonify({ "success": True, "data": enriched_data }), 200

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({ "success": False, "message": "Error fetching data" }), 500

def get_activity_ai(model):
    data = request.get_json()

    # เพิ่มรับ user_info และ processJson
    # user_info = data.get("user_info")
    # processJson = data.get("processJson")
    
    user_sys_id = data.get("user_sys_id")
    
    jsonInfo = callJson(user_sys_id)

    keys = [
        "activity_id", "title", "create_date", "start_date", "end_date",
        "status", "create_by", "location_id", "location_name", "location_type", "flag_valid"
    ]

    if not any(data.get(k) for k in keys):
        return jsonify({ "success": False, "message": "No value input!" }), 404

    query = """
    SELECT * FROM activity a
    LEFT JOIN location l ON l.location_id = a.location_id
    WHERE a.activity_id > 0
    """

    for key in keys:
        value = data.get(key)
        if value is not None:
            if isinstance(value, str):
                query += f" AND {alias_prefix(key)}.{key} = '{value}' \n"
            else:
                query += f" AND {alias_prefix(key)}.{key} = {value} \n"

    limit = data.get('limit')
    if limit :
        query += "LIMIT 10"
    
    print(query)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ดึง activity หลัก
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        if not rows:
            cur.close()
            conn.close()
            return jsonify({ "success": True, "data": [] }), 200

        # ---------- ดึงข้อมูลเสริม ----------
        activity_ids = [row["activity_id"] for row in rows]
        placeholders = ",".join(map(str, activity_ids))

        # ดึง activity_type_normalize
        query_type = f"""
        SELECT * FROM public.activity_type_normalize atn
        LEFT JOIN activity_type at ON at.activity_type_id = atn.activity_type_id
        WHERE atn.activity_id IN ({placeholders})
        """
        cur.execute(query_type)
        type_columns = [desc[0] for desc in cur.description]
        type_data = [dict(zip(type_columns, row)) for row in cur.fetchall()]

        # ดึง activity_subject_normalize
        query_subject = f"""
        SELECT * FROM public.activity_subject_normalize asn
        LEFT JOIN subject s ON s.subject_id = asn.subject_id
        WHERE asn.activity_id IN ({placeholders})
        """
        cur.execute(query_subject)
        subject_columns = [desc[0] for desc in cur.description]
        subject_data = [dict(zip(subject_columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()

        # ---------- จัดกลุ่ม ----------
        ac_type_grouped = {}
        for row in type_data:
            aid = row['activity_id']
            ac_type_grouped.setdefault(aid, []).append(row)

        sub_type_grouped = {}
        for row in subject_data:
            aid = row['activity_id']
            sub_type_grouped.setdefault(aid, []).append(row)

        # ---------- สร้าง enriched_data ----------
        enriched_data = []
        for activity in rows:
            aid = activity['activity_id']
            enriched_data.append({
                **activity,
                "activity_type_data": ac_type_grouped.get(aid, []),
                "activity_subject_data": sub_type_grouped.get(aid, [])
            })

        print("sima")

        prediction_data = predict_lgbm(jsonInfo, model)
        
        print("prediction_data", prediction_data)

        
        rank_map = {v: k for k, v in prediction_data.items()}
        enriched_data_sorted = sorted(enriched_data, key=lambda activity: get_rank(activity, rank_map))


        return jsonify({ "success": True, "data": enriched_data_sorted }), 200

    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({ "success": False, "message": "Error fetching data" }), 500


def alias_prefix(key):
    # แยก prefix ให้ตรงกับ table alias
    activity_keys = [
        "activity_id", "title", "create_date", "start_date", "end_date",
        "status", "create_by", "flag_valid", "location_id"
    ]
    if key in activity_keys:
        return "a"
    elif key in ["location_name", "location_type"]:
        return "l"
    return ""


def get_rank(activity, rank_map):
    # ดึงประเภทกิจกรรมจาก activity_type_data[0] (ถ้ามีหลายรายการอาจเลือกวิธีอื่น)
    if activity.get('activity_type_data'):
        # ลองดึง activity_type_name_th
        name_th = activity['activity_type_data'][0].get('activity_type_name_th', '').strip()
        # หาค่า rank จาก map
        return rank_map.get(name_th, 9999)  # 9999 = ค่า default ถ้าไม่เจอประเภท
    return 9999