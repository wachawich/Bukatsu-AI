from db.db_connection import get_db_connection

def getFavActivityType(user_sys_id):
    query = """
        SELECT ats.activity_type_name_th from favorite_normalize fn
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