import psycopg2
import os
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def get_db_connection_AI():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST_AI"),
        database=os.getenv("DB_NAME_AI"),
        user=os.getenv("DB_USER_AI"),
        password=os.getenv("DB_PASSWORD_AI")
    )
    return conn

def pgQuery(query):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)