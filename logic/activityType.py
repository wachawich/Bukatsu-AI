from flask import request, jsonify
from db.db_connection import get_db_connection

def getActivityType():
    
    query = """
        select activity_type_name_th from activity_type 
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
        select ats.activity_type_name_th from activity_interest_normalize ain 
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