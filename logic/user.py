from flask import request, jsonify
from db.db_connection import get_db_connection

def get_user(user_sys_id):
    query = """
    SELECT * FROM user_sys us
    LEFT JOIN role r ON r.role_id = us.role_id
    LEFT JOIN org o ON o.org_id = us.org_id
    WHERE us.user_sys_id > 0 AND us.user_sys_id = %s
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
