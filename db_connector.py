import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수 로드
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"), 
    "database": os.getenv("MYSQL_DATABASE")
}

def get_db_connection():
    """
    MySQL 데이터베이스 커넥션을 생성하여 반환합니다.

    Returns:
        mysql.connector.connection.MySQLConnection or None: 
        연결 성공 시 커넥션 객체, 실패 시 None 반환.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"FATAL ERROR - MySQL Connection: {err}")
        return None

def execute_procedure(procedure_name):
    """
    지정된 이름의 저장 프로시저(Stored Procedure)를 실행합니다.

    Args:
        procedure_name (str): 실행할 프로시저의 이름

    Returns:
        tuple: (성공 여부 bool, 메시지 str)
    """
    conn = get_db_connection()
    if conn is None: return False, "DB 연결 실패"
    
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
    SELECT 쿼리를 실행하고 결과를 딕셔너리 형태로 반환합니다.

    Args:
        query (str): 실행할 SQL 쿼리문
        params (tuple, optional): 쿼리에 바인딩할 파라미터 튜플

    Returns:
        tuple: (결과 리스트 list or None, 에러 메시지 str or None)
    """
    conn = get_db_connection()
    if conn is None: return None, "DB 연결 실패"
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result, None 
    except mysql.connector.Error as err:
        return None, str(err)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_application(data):
    """
    신청서 데이터를 받아 HOUSEHOLD, USER, FINANCIAL_INFO 3개 테이블에 분산 저장합니다.
    USER와 HOUSEHOLD 간의 순환 참조 문제를 해결하기 위해 외래키 검사를 일시 해제합니다.

    Args:
        data (dict): 프론트엔드에서 전송받은 신청 데이터

    Returns:
        tuple: (성공 여부 bool, 메시지 str)
    """
    conn = get_db_connection()
    if conn is None: return False, "DB 연결 실패"
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 순환 참조(USER <-> HOUSEHOLD) 저장을 위해 외래키 검사 비활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")

        # 1. 데이터 파싱 및 전처리
        u_id = data['user_id']
        h_id = f"H_{u_id}"   # 가구 ID 생성
        f_id = f"F_{u_id}"   # 재무 정보 ID 생성
        
        # 사용자 정보
        name = data.get('name')
        birth_date = data.get('birth_date')
        address = data.get('address')
        
        # 가구 정보
        members = int(data.get('family_count', 1))
        income_type = data.get('income_type')
        qual_code = data.get('qual_code')
        is_single_adj = 1 if members == 1 else 0  # 1인 가구 조정값
        
        # 재무 정보 (판정 로직용 합산 데이터 계산)
        sub_type = data.get('sub_type')
        earned_income = int(data.get('income', 0))
        fin_income = int(data.get('fin_income', 0))
        total_income = earned_income + fin_income        # 총 소득
        total_assets = int(data.get('assets', 0))        # 재산세 과세표준
        hi_premium = int(data.get('hi_premium', 0))      # 건보료

        # 2. HOUSEHOLD 테이블 저장 (INSERT / UPDATE)
        sql_household = """
            INSERT INTO HOUSEHOLD 
            (HOUSEHOLD_ID, HEAD_USER_ID, MEMBER_COUNT, INCOME_SOURCE_TYPE, QUALIFICATION_CODE, SINGLE_PERSON_ADJ) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                MEMBER_COUNT=%s, INCOME_SOURCE_TYPE=%s, QUALIFICATION_CODE=%s, SINGLE_PERSON_ADJ=%s
        """
        cursor.execute(sql_household, (
            h_id, u_id, members, income_type, qual_code, is_single_adj, 
            members, income_type, qual_code, is_single_adj
        ))

        # 3. USER 테이블 저장 (INSERT / UPDATE)
        sql_user = """
            INSERT INTO USER 
            (USER_ID, NAME, BIRTH_DATE, ADDRESS, HOUSEHOLD_ID) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                NAME=%s, BIRTH_DATE=%s, ADDRESS=%s, HOUSEHOLD_ID=%s
        """
        cursor.execute(sql_user, (
            u_id, name, birth_date, address, h_id, 
            name, birth_date, address, h_id
        ))

        # 4. FINANCIAL_INFO 테이블 저장 (INSERT / UPDATE)
        sql_finance = """
            INSERT INTO FINANCIAL_INFO 
            (INFO_ID, USER_ID, SUBSCRIBER_TYPE, TOTAL_INCOME, FINANCIAL_INCOME_SUM, PROPERTY_TAX_BASE_SUM, HEALTH_INSURANCE_PREMIUM) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                SUBSCRIBER_TYPE=%s, TOTAL_INCOME=%s, FINANCIAL_INCOME_SUM=%s, PROPERTY_TAX_BASE_SUM=%s, HEALTH_INSURANCE_PREMIUM=%s
        """
        cursor.execute(sql_finance, (
            f_id, u_id, sub_type, total_income, fin_income, total_assets, hi_premium,
            sub_type, total_income, fin_income, total_assets, hi_premium
        ))

        # 작업 완료 후 외래키 검사 재활성화 및 커밋
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
        return True, "저장 성공"
        
    except mysql.connector.Error as err:
        if conn: conn.rollback()
        print(f"Insert Error: {err}")
        return False, str(err)
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()