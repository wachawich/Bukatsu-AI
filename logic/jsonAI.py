from flask import request, jsonify
import json
from datetime import datetime
from db.db_connection import get_db_connection, get_db_connection_AI
from logic.processJsonInfo import processFunctionLocal

from flask import jsonify
import json
from datetime import datetime

from psycopg2.extras import Json

def callJson(user_sys_id):
    try:
        if not user_sys_id:
            return False
        
        print(user_sys_id)

        conn = get_db_connection_AI()
        cur = conn.cursor()

        # 1. ตรวจสอบว่ามี user_sys_id นี้อยู่หรือไม่
        cur.execute("""
            SELECT json_info FROM json_collection
            WHERE user_sys_id = %s AND (flag_valid = TRUE OR flag_valid = 'Y')
        """, (user_sys_id,))
        result = cur.fetchone()

        if result:
            json_info = result[0]
            cur.close()
            conn.close()
            return json_info

        # 2. ถ้าไม่มี → insert default
        # 2. ถ้าไม่มี → insert default
        default_json = processFunctionLocal(user_sys_id)

        json_str = json.dumps(default_json, ensure_ascii=False)

        cur.execute("""
            INSERT INTO json_collection (user_sys_id, json_info, flag_valid, update_time)
            VALUES (%s, %s, %s, %s)
        """, (user_sys_id, json_str, True, datetime.utcnow()))

        conn.commit()
        cur.close()
        conn.close()

        return default_json

    except Exception as e:
        print("Error in callJson:", e)
        return False
    
    
def callJsonAPI():
    data = request.get_json()
    
    try:
        if not data['user_sys_id']:
            return jsonify({ "success": False, "message": "Missing user_sys_id" }), 400

        conn = get_db_connection_AI()
        cur = conn.cursor()

        # 1. ตรวจสอบว่ามี user_sys_id นี้อยู่หรือไม่
        cur.execute("""
            SELECT json_info FROM json_collection
            WHERE user_sys_id = %s AND (flag_valid = TRUE OR flag_valid = 'Y')
        """, (data['user_sys_id'],))
        result = cur.fetchone()

        if result:
            json_info = result[0]
            cur.close()
            conn.close()
            return jsonify({ "success": True, "data": json_info }), 200

        # 2. ถ้าไม่มี → insert default
        default_json = processFunctionLocal(data['user_sys_id'])

        json_str = json.dumps(default_json, ensure_ascii=False)

        cur.execute("""
            INSERT INTO json_collection (user_sys_id, json_info, flag_valid, update_time)
            VALUES (%s, %s, %s, %s)
        """, (data['user_sys_id'], json_str, True, datetime.utcnow()))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({ 
            "success": True, 
            "data": default_json, 
            "message": "Created default json_info for user" 
        }), 201

    except Exception as e:
        print("Error in callJson:", e)
        return jsonify({ "success": False, "message": "Error processing request" }), 500    



import json
from datetime import datetime

# def updateJsonField():
#     try:
#         data = request.get_json()

#         user_sys_id = data.get('user_sys_id')
#         section = data.get('section')
#         activity_name = data.get('activity_name')
        
#         print(user_sys_id)

#         if not user_sys_id or not section or not activity_name:
#             return jsonify({"success": False, "message": "Missing required fields"}), 400

#         conn = get_db_connection_AI()
#         cur = conn.cursor()

#         cur.execute("""
#             SELECT json_info FROM json_collection
#             WHERE user_sys_id = %s AND (flag_valid = TRUE OR flag_valid = 'Y')
#         """, (user_sys_id,))
#         result = cur.fetchone()

#         if not result:
#             return jsonify({"success": False, "message": "user_sys_id not found"}), 404

#         json_info_raw = result[0]

#         if isinstance(json_info_raw, str):
#             json_info = json.loads(json_info_raw)
#         else:
#             json_info = json_info_raw
            
            
#         if section not in json_info:
#             json_info[section] = {}
#         if activity_name not in json_info[section]:
#             json_info[section][activity_name] = 0

#         # เพิ่มค่า
#         json_info[section][activity_name] += 1

#         # แปลงกลับเป็น JSON string
#         json_str = json.dumps(json_info, ensure_ascii=False)

#         # อัปเดตฐานข้อมูล
#         cur.execute("""
#             UPDATE json_collection
#             SET json_info = %s, update_time = %s
#             WHERE user_sys_id = %s
#         """, (json_str, datetime.utcnow(), user_sys_id))

#         conn.commit()
#         cur.close()
#         conn.close()

#         return jsonify({"success": True, "updated_json": json_info})

#     except Exception as e:
#         print("Error in /update_json:", e)
#         return jsonify({"success": False, "message": str(e)}), 500


def updateJsonField():
    try:
        data = request.get_json()

        user_sys_id = data.get('user_sys_id')
        section = data.get('section')
        activity_id = data.get('activity_id')

        if not user_sys_id or not section or not activity_id:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        # ถัง B: ดึง activity_type_name จาก activity_id
        conn_act = get_db_connection()
        cur_act = conn_act.cursor()

        cur_act.execute("""
            SELECT at.activity_type_name_th \n
            FROM activity a \n
            JOIN activity_type_normalize atn ON a.activity_id = atn.activity_id \n
            JOIN activity_type at ON atn.activity_type_id = at.activity_type_id \n
            WHERE a.activity_id = %s
        """, (activity_id,))
        activity_types = cur_act.fetchall()
        cur_act.close()
        conn_act.close()

        if not activity_types:
            return jsonify({"success": False, "message": "activity_id not found"}), 404

        # ถัง A: ดึง json_info จาก user_sys_id
        conn_json = get_db_connection_AI()
        cur_json = conn_json.cursor()

        cur_json.execute("""
            SELECT json_info FROM json_collection
            WHERE user_sys_id = %s AND (flag_valid = TRUE OR flag_valid = 'Y')
        """, (user_sys_id,))
        result = cur_json.fetchone()

        if not result:
            cur_json.close()
            conn_json.close()
            return jsonify({"success": False, "message": "user_sys_id not found"}), 404

        json_info_raw = result[0]
        if isinstance(json_info_raw, str):
            json_info = json.loads(json_info_raw)
        else:
            json_info = json_info_raw

        # อัปเดตข้อมูล
        if section not in json_info:
            json_info[section] = {}

        for (activity_type_name_th,) in activity_types:
            if activity_type_name_th not in json_info[section]:
                json_info[section][activity_type_name_th] = 0
            json_info[section][activity_type_name_th] += 1

        json_str = json.dumps(json_info, ensure_ascii=False)

        cur_json.execute("""
            UPDATE json_collection
            SET json_info = %s, update_time = %s
            WHERE user_sys_id = %s
        """, (json_str, datetime.utcnow(), user_sys_id))

        conn_json.commit()
        cur_json.close()
        conn_json.close()

        return jsonify({"success": True, "updated_json": json_info})

    except Exception as e:
        print("Error in /update_json:", e)
        return jsonify({"success": False, "message": str(e)}), 500

