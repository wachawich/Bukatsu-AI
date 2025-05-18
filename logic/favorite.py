from db.db_connection import get_db_connection

# def get_fav():
#     data = request.get_json()

#     user_sys_id = data.get("user_sys_id")
#     activity_id = data.get("activity_id")
#     flag_valid = data.get("flag_valid")

#     if not user_sys_id and not activity_id and not flag_valid:
#         return jsonify({ "success": False, "message": "No value Input" }), 400

#     query = """
#     SELECT * FROM favorite_normalize fn
#     LEFT JOIN activity a ON a.activity_id = fn.activity_id
#     LEFT JOIN activity_type at ON at.activ
#     WHERE fn.user_sys_id > 0
#     """

#     if user_sys_id:
#         query += f" AND fn.user_sys_id = {user_sys_id} \n"
#     if activity_id:
#         query += f" AND fn.activity_id = {activity_id} \n"
#     if flag_valid:
#         query += f" AND fn.flag_valid = {flag_valid} \n"

#     print(query)

#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute(query)
#         columns = [desc[0] for desc in cur.description]
#         rows = [dict(zip(columns, row)) for row in cur.fetchall()]
#         cur.close()
#         conn.close()
#         return jsonify({ "success": True, "data": rows }), 200
#     except Exception as e:
#         print("Error fetching data:", e)
#         return jsonify({ "success": False, "message": "Error fetching data" }), 500


def getFavActivityType(user_sys_id):
    query = """
        SELECT ats.activity_type_name from favorite_normalize fn
        LEFT JOIN activity a ON a.activity_id = fn.activity_id
        LEFT JOIN activity_type_normalize atn ON atn.activity_id = a.activity_id
        LEFT JOIN activity_type ats ON ats.activity_type_id = atn.activity_type_id
        WHERE fn.user_sys_id = %s
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
        return rows

    except Exception as e:
        print("Error fetching data:", e)
        return []