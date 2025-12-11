import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수 설정
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"), 
    "database": os.getenv("MYSQL_DATABASE")
}

def get_db_connection():
    """MySQL 데이터베이스 연결 객체를 반환합니다."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"FATAL ERROR - MySQL Connection: {err}")
        return None

def execute_procedure(procedure_name):
    """저장 프로시저를 실행합니다."""
    conn = get_db_connection()
    if conn is None: 
        return False, "DB 연결 실패"
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.callproc(procedure_name)
        conn.commit()
        return True, "성공"
    except mysql.connector.Error as err:
        return False, str(err)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def fetch_data(query, params=None):
    """
    SQL 쿼리를 실행하고 결과를 반환합니다.
    반환값: (결과_리스트, 에러_메시지)
    """
    conn = get_db_connection()
    if conn is None: 
        return None, "DB 연결 실패"
    
    cursor = None
    try:
        # dictionary=True로 설정해야 컬럼명으로 데이터 접근 가능
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = cursor.fetchall()
        
        # ★ 중요: 반드시 (데이터, None) 형태의 튜플을 반환해야 함
        return result, None 
        
    except mysql.connector.Error as err:
        # 에러 발생 시 (None, 에러메시지) 반환
        print(f"Query Error: {err}")
        return None, str(err)
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()