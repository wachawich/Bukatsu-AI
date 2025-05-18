from flask import request, jsonify
from db.db_connection import get_db_connection

def get_activity(activity_ids):
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


def get_activity_withFav(activity_ids):
    data = request.get_json()

    keys = [
        "user_sys_id", "activity_id", "title", "create_date", "start_date", "end_date",
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



def getActivityType():
    
    query = """
        select activity_type_name from activity_type 
        WHERE flag_valid = true
    """
    
    print(query)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return rows

    except Exception as e:
        print("Error fetching data:", e)
        return []
    
    
def getActivityTypeInteresting(user_sys_id):
    
    if user_sys_id is None :
        return
    
    query = """
        select activity_type_name from activity_interest_normalize ain 
        LEFT JOIN activity_type ats ON ats.activity_type_id = ain.activity_type_id
        WHERE ain.flag_valid = true AND ain.user_sys_id = %s
    """
    
    print(query)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_sys_id,))
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        print("row", rows)
        return rows

    except Exception as e:
        print("Error fetching data:", e)
        return []