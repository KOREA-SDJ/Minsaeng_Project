from flask import Flask, jsonify, request, render_template
from db_connector import execute_procedure, fetch_data, get_db_connection, insert_application
import os

# 서버 시작 전 DB 연결 상태 진단
conn_check = get_db_connection()
if conn_check:
    print("----- DEBUG: DB 연결 성공! Flask 서버를 시작합니다. -----")
    conn_check.close()
else:
    raise RuntimeError("FATAL ERROR: DB 연결 실패. .env 파일 설정과 MySQL 실행 여부를 확인하세요.")

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    신청서 작성 메인 페이지를 렌더링합니다.

    Returns:
        str: 'form.html' 템플릿 렌더링 결과
    """
    return render_template('form.html')

@app.route('/result')
def result_page():
    """
    판정 결과 조회 페이지를 렌더링합니다.
    신청 완료 후 또는 조회 시 이동되는 페이지입니다.

    Returns:
        str: 'index.html' 템플릿 렌더링 결과
    """
    return render_template('index.html')

@app.route('/apply')
def apply_page():
    """
    신청서 작성 페이지의 별칭(Alias) 라우트입니다.

    Returns:
        str: 'form.html' 템플릿 렌더링 결과
    """
    return render_template('form.html')

@app.route('/api/apply', methods=['POST'])
def process_application():
    """
    프론트엔드에서 전송한 신청 데이터를 받아 DB에 저장하고,
    즉시 판정 로직(Stored Procedure)을 실행합니다.

    1. JSON 데이터 수신
    2. DB 신청 정보 저장 (INSERT)
    3. 자격 판정 프로시저 실행 (SP_RUN_DETERMINATION)

    Returns:
        tuple: (JSON 응답 객체, HTTP 상태 코드)
            - success: {'status': 'success', ...} (200)
            - error: {'status': 'error', ...} (500)
    """
    # 1. 프론트엔드 데이터 수신
    data = request.get_json()
    
    # 2. DB 저장 시도
    success, msg = insert_application(data)
    if not success:
        return jsonify({'status': 'error', 'message': f'데이터 저장 실패: {msg}'}), 500
        
    # 3. 판정 로직 즉시 실행
    proc_success, proc_msg = execute_procedure("SP_RUN_DETERMINATION")
    
    if not proc_success:
        return jsonify({'status': 'error', 'message': f'판정 실행 실패: {proc_msg}'}), 500
        
    return jsonify({'status': 'success', 'message': '신청 및 판정 완료', 'user_id': data['user_id']}), 200

@app.route('/api/run-determination', methods=['POST'])
def run_determination():
    """
    관리자용 API: 판정 로직(SP_RUN_DETERMINATION)을 수동으로 실행합니다.

    Returns:
        tuple: (JSON 응답 객체, HTTP 상태 코드)
    """
    success, message = execute_procedure("SP_RUN_DETERMINATION")
    if success:
        return jsonify({"status": "success", "message": "판정 로직 재계산 및 갱신 완료"}), 200
    else:
        return jsonify({"status": "error", "message": f"판정 실행 실패: {message}"}), 500

@app.route('/api/result/<user_id>', methods=['GET'])
def get_user_result(user_id):
    """
    특정 사용자의 최종 판정 결과를 조회합니다.
    DB View(V_FINAL_REPORT)를 기반으로 데이터를 가져옵니다.

    Args:
        user_id (str): 조회할 사용자의 고유 ID

    Returns:
        tuple: (JSON 응답 객체, HTTP 상태 코드)
            - success: 200 OK, 데이터 포함
            - not_found: 404 Not Found, ID 없음
            - error: 500 Server Error, DB 오류
    """
    query = "SELECT * FROM V_FINAL_REPORT WHERE 사용자_ID = %s"
    data, error = fetch_data(query, (user_id,))
    
    if error:
        return jsonify({"status": "error", "message": f"데이터 조회 실패: {error}"}), 500
    
    if data:
        return jsonify({"status": "success", "data": data[0]}), 200
    else:
        return jsonify({"status": "not_found", "message": "사용자 ID를 찾을 수 없거나 판정 결과가 없습니다."}), 404

if __name__ == '__main__':
    os.environ['PYTHONIOENCODING'] = 'utf-8' 
    os.environ['FLASK_RUN_HOST'] = '0.0.0.0' 
    app.run(debug=True)