from flask import Flask, jsonify, request, render_template
from db_connector import execute_procedure, fetch_data, get_db_connection # <-- get_db_connection 추가!
import os

# --- [진단 코드 START] ---
conn_check = get_db_connection()
if conn_check:
    print("----- DEBUG: DB 연결 성공! Flask 서버를 시작합니다. -----")
    conn_check.close()
else:
    # 연결 실패 시 서버 시작을 막고 에러 메시지를 터미널에 출력합니다.
    raise RuntimeError("FATAL ERROR: DB Connection Failed. Check credentials in .env and ensure MySQL is running.")
# --- [진단 코드 END] ---

app = Flask(__name__)

# --- API 엔드포인트 정의 ---
@app.route('/', methods=['GET'])
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/api/run-determination', methods=['POST'])
def run_determination():
    """
    관리자 요청: SP_RUN_DETERMINATION 저장 프로시저를 실행하여
    전체 시스템의 판정 결과를 갱신합니다.
    """
    # 저장 프로시저 호출 (DB 내에서 판정 로직 실행)
    success, message = execute_procedure("SP_RUN_DETERMINATION")
    
    if success:
        # 200 OK 응답
        return jsonify({"status": "success", "message": "판정 로직 재계산 및 갱신 완료"}), 200
    else:
        # 500 Internal Server Error 응답
        return jsonify({"status": "error", "message": f"판정 실행 실패: {message}"}), 500

@app.route('/api/result/<user_id>', methods=['GET'])
def get_user_result(user_id):
    """
    사용자 마이페이지: 최종 V_FINAL_REPORT 뷰에서 결과를 조회합니다.
    """
    # V_FINAL_REPORT 뷰에서 특정 사용자 ID의 결과 조회
    query = "SELECT * FROM V_FINAL_REPORT WHERE 사용자_ID = %s"
    data, error = fetch_data(query, (user_id,))
    
    if error:
        return jsonify({"status": "error", "message": f"데이터 조회 실패: {error}"}), 500
    
    if data:
        # 데이터가 있으면 첫 번째 행 반환
        return jsonify({"status": "success", "data": data[0]}), 200
    else:
        # 데이터가 없으면 404 Not Found 응답
        return jsonify({"status": "not_found", "message": "사용자 ID를 찾을 수 없거나 판정 결과가 없습니다."}), 404

# --- 서버 실행 및 환경 설정 ---

if __name__ == '__main__':
    # Flask 내부 실행 대신, python app.py 명령어가 서버를 직접 띄우도록 변경
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8' 
    os.environ['FLASK_RUN_HOST'] = '0.0.0.0' 
    app.run(debug=True) # host='0.0.0.0'는 환경 변수로 처리됨

