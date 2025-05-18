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

