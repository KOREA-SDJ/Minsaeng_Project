# 💰 민생지원금 자격 판정 시스템 (Public Livelihood Support System)

사용자의 소득, 자산, 건강보험료 정보를 기반으로 민생지원금 지급 대상 여부를 자동으로 판정하고, 예상 지급액을 계산해주는 웹 애플리케이션입니다.

## 📌 프로젝트 소개
이 프로젝트는 복잡한 복지 정책 기준을 데이터베이스 로직(Stored Procedure)으로 구현하여, 신청 즉시 실시간으로 결과를 확인할 수 있도록 설계되었습니다.

### 주요 기능
* **신청서 작성**: 사용자 기본 정보, 가구 정보, 소득 및 재산 정보를 입력받습니다.
    * *편의 기능*: 만 19세 미만 신청 제한, 입력 금액 한글 자동 변환 표시.
* **자격 자동 판정**: 입력된 데이터를 바탕으로 지급/탈락 여부를 즉시 계산합니다.
    * 기준: 소득(근로+금융), 자산(재산세 과세표준), 건강보험료 납부액.
* **결과 조회**: 판정 번호, 최종 결과(합격/불합격), 지급 예정액, 탈락 시 상세 사유를 시각적으로 제공합니다.
* **데이터 관리**: 신청 내역을 MySQL 데이터베이스에 체계적으로 저장하고 관리합니다.

---

## 🛠 기술 스택 (Tech Stack)

* **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
* **Backend**: Python, Flask
* **Database**: MySQL 8.0+
* **Deployment**: Localhost (Development)

---

## ⚙️ 설치 및 실행 방법 (Installation)

### 1. 프로젝트 클론 (Clone)

git clone [https://github.com/KOREA-SDJ/minsaeng-project.git](https://github.com/KOREA-SDJ/minsaeng-project.git)
cd minsaeng-project

### 2. 가상 환경 설정 및 패키지 설치


# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
source venv/Scripts/activate

# 가상 환경 활성화 (Mac/Linux)
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r requirements.txt

### 3. 데이터베이스 설정 (MySQL)
프로젝트에 포함된 SQL 파일들을 **아래 순서대로** 실행하여 DB 구조를 생성해야 합니다.

* **`schema.sql`**: 데이터베이스 및 테이블 생성
* **`data.sql`**: 기준표(정책 기준) 및 기초 데이터 삽입
* **`procedures.sql`**: 판정 로직(Stored Procedure) 생성
* **`views.sql`**: 결과 조회용 뷰(View) 생성


4. 환경 변수 설정 (.env)프로젝트 루트 경로에 .env 파일을 생성하고, 본인의 DB 접속 정보를 아래와 같이 입력하세요.Ini, TOMLMYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=본인의_비밀번호
MYSQL_DATABASE=minsaeng
5. 서버 실행다음 명령어를 사용하여 서버를 실행합니다.Bashpython app.py
서버가 정상적으로 실행되면 브라우저에서 http://127.0.0.1:5000 으로 접속합니다.📂 프로젝트 구조프로젝트 폴더 구조는 다음과 같습니다.Plaintextminsaeng-project/
├── app.py              # Flask 메인 애플리케이션 (라우팅, API)
├── db_connector.py     # DB 연결 및 쿼리 실행 모듈
├── schema.sql          # DB 스키마 정의
├── data.sql            # 초기 데이터 및 정책 기준
├── procedures.sql      # 판정 로직 프로시저 (SP_RUN_DETERMINATION)
├── views.sql           # 결과 보고서 뷰 (V_FINAL_REPORT)
├── templates/
│   ├── form.html       # 신청서 작성 페이지
│   └── index.html      # 결과 조회 페이지
├── .env                # 환경 변수 (Git 제외)
├── .gitignore          # Git 제외 파일 목록
└── README.md           # 프로젝트 설명서
📊 판정 로직 (Logic)SP_RUN_DETERMINATION 저장 프로시저를 통해 다음 순서로 판정이 이루어집니다.1. 자격 요건 검사아래 3가지 조건을 모두 만족해야 합니다.총 소득(근로 + 금융) $\le$ 2,000만 원재산세 과세표준 합산액 $\le$ 12억 원건강보험료 납부액 $\le$ 가구원수별 기준표 상한액 (예: 1인 외벌이 22만 원)2. 지급액 산정자격 요건 통과 시, 신청자의 복지 자격에 따라 차등 지급합니다.복지 자격지급액기초생활수급자500,000원차상위계층400,000원일반 시민250,000원3. 결과 저장판정 번호 생성(날짜 + 일련번호) 및 결과를 DETERMINATION 테이블에 저장합니다.