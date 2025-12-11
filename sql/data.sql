-- ----------------------------------------------------------------
-- 0. 데이터베이스 선택 및 트랜잭션 시작
-- ----------------------------------------------------------------
USE minsaeng;
START TRANSACTION;

-- ----------------------------------------------------------------
-- 1. 기준표 및 메타데이터 삽입 (부모 테이블)
-- ----------------------------------------------------------------

-- REJECTION_REASON (탈락 사유 코드 정의)
INSERT INTO REJECTION_REASON (REASON_CODE, REASON_TYPE, REASON_DESCRIPTION) VALUES
('ASSET_EXCESS', '재산 초과', '재산세 과세 표준 합산액이 정책 기준을 초과함'),
('FINANCIAL_EXCESS', '소득 초과', '총 소득 또는 금융 소득 합산액이 기준을 초과함'),
('HI_PREMIUM_EXCESS', '보험료 초과', '건강보험료 납부액이 가구원수별 상한 기준을 초과함'),
('DUPLICATE_RECEIPT', '중복 수령', '타 지자체 또는 유사 복지 사업에서 이미 수령함');


-- POLICY_CRITERIA (정책 기준 및 지급액)
INSERT INTO POLICY_CRITERIA (
    CRITERIA_ID, POLICY_NAME, PROPERTY_TAX_LIMIT, FINANCIAL_INCOME_LIMIT,
    BASIC_RECIPIENT_BASE, SUB_BASIC_BASE, GENERAL_CITIZEN_BASE, TOP_10_BASE
) VALUES
('P2025-1', '2025년 1차 민생지원금', 1200000000, 20000000,
 500000, 400000, 250000, 150000);


-- HEALTH_INSURANCE_CRITERIA (건보료 상한 기준표)
INSERT INTO HEALTH_INSURANCE_CRITERIA (
    HI_CRIT_ID, CRITERIA_ID, HOUSEHOLD_TYPE, MEMBER_COUNT_TYPE, SUBSCRIBER_TYPE, PREMIUM_UPPER_LIMIT
) VALUES
-- 외벌이 기준
('HIC01WJ', 'P2025-1', '외벌이', '1', '직장', 220000), ('HIC01WL', 'P2025-1', '외벌이', '1', '지역', 220000), ('HIC01WH', 'P2025-1', '외벌이', '1', '혼합', 220000),
('HIC02WJ', 'P2025-1', '외벌이', '2', '직장', 330000), ('HIC02WL', 'P2025-1', '외벌이', '2', '지역', 310000), ('HIC02WH', 'P2025-1', '외벌이', '2', '혼합', 330000),
('HIC03WJ', 'P2025-1', '외벌이', '3', '직장', 420000), ('HIC03WL', 'P2025-1', '외벌이', '3', '지역', 390000), ('HIC03WH', 'P2025-1', '외벌이', '3', '혼합', 420000),
('HIC04WJ', 'P2025-1', '외벌이', '4', '직장', 510000), ('HIC04WL', 'P2025-1', '외벌이', '4', '지역', 500000), ('HIC04WH', 'P2025-1', '외벌이', '4', '혼합', 520000),
-- 다소득원 기준 (1인 가구 포함, 최종 확인 데이터)
('HIC01MJ', 'P2025-1', '다소득원', '1', '직장', 270000), ('HIC01ML', 'P2025-1', '다소득원', '1', '지역', 260000), ('HIC01MH', 'P2025-1', '다소득원', '1', '혼합', 280000),
('HIC02MJ', 'P2025-1', '다소득원', '2', '직장', 420000), ('HIC02ML', 'P2025-1', '다소득원', '2', '지역', 390000), ('HIC02MH', 'P2025-1', '다소득원', '2', '혼합', 420000),
('HIC03MJ', 'P2025-1', '다소득원', '3', '직장', 510000), ('HIC03ML', 'P2025-1', '다소득원', '3', '지역', 500000), ('HIC03MH', 'P2025-1', '다소득원', '3', '혼합', 520000),
('HIC04MJ', 'P2025-1', '다소득원', '4', '직장', 600000), ('HIC04ML', 'P2025-1', '다소득원', '4', '지역', 590000), ('HIC04MH', 'P2025-1', '다소득원', '4', '혼합', 620000);


-- ----------------------------------------------------------------
-- 2. 테스트 사용자 및 가구 정보 삽입 (FK 순서 중요)
-- ----------------------------------------------------------------

-- 2.1. HOUSEHOLD 테이블 (USER 테이블에 의해 참조되므로 먼저 삽입)
INSERT INTO HOUSEHOLD (
    HOUSEHOLD_ID, HEAD_USER_ID, MEMBER_COUNT, INCOME_SOURCE_TYPE, QUALIFICATION_CODE, SINGLE_PERSON_ADJ
) VALUES
('H001', 'U001', 4, '외벌이', 'GENERAL', 0), ('H002', 'U003', 2, '다소득원', 'SUBBASIC', 0), ('H003', 'U004', 1, '외벌이', 'TOP10', 1), 
('H004', 'U005', 3, '외벌이', 'BASIC', 0), ('H005', 'U006', 2, '다소득원', 'GENERAL', 0), ('H007', 'U007', 2, '외벌이', 'GENERAL', 0),
('H008', 'U008', 1, '다소득원', 'GENERAL', 1), ('H009', 'U009', 1, '다소득원', 'GENERAL', 1), ('H010', 'U010', 2, '다소득원', 'GENERAL', 0),
('H011', 'U011', 4, '외벌이', 'GENERAL', 0), ('H012', 'U012', 3, '외벌이', 'GENERAL', 0), ('H013', 'U013', 2, '다소득원', 'TOP10', 0),
('H014', 'U014', 1, '외벌이', 'GENERAL', 1), ('H015', 'U015', 3, '외벌이', 'GENERAL', 0);


-- 2.2. USER 테이블
-- (HOUSEHOLD 테이블이 먼저 채워졌으므로 FK 오류 없이 삽입 가능)
INSERT INTO USER (USER_ID, NAME, BIRTH_DATE, ADDRESS, HOUSEHOLD_ID) VALUES
('U001', '김철수', '1985-01-01', '서울시 종로구', 'H001'), ('U002', '이영희', '1987-02-02', '서울시 종로구', 'H001'),
('U003', '박민지', '1990-03-03', '서울시 용산구', 'H002'), ('U004', '최고가', '1975-04-04', '경기도 성남시', 'H003'),
('U005', '나기초', '1995-05-05', '인천시 연수구', 'H004'), ('U006', '김맞벌', '1988-06-06', '부산시 해운대구', 'H005'),
('U007', '임혼합', '1990-07-07', '대구시 수성구', 'H007'), ('U008', '정재산', '1985-08-08', '광주시 남구', 'H008'),
('U009', '이지역', '1995-09-09', '대전시 서구', 'H009'), ('U010', '김부부', '1988-10-10', '울산시 남구', 'H010'),
('U011', '정초과', '1970-11-11', '세종시 한솔동', 'H011'), ('U012', '한여유', '1982-12-12', '제주시 연동', 'H012'),
('U013', '상위금', '1980-01-01', '서울시 강남구', 'H013'), ('U014', '소득초', '1992-02-02', '부산시 동래구', 'H014'),
('U015', '보험료초', '1975-03-03', '대구시 북구', 'H015');


-- 2.3. FINANCIAL_INFO 테이블
-- (USER 테이블이 먼저 채워졌으므로 FK 오류 없이 삽입 가능)
INSERT INTO FINANCIAL_INFO (
    INFO_ID, USER_ID, SUBSCRIBER_TYPE, TOTAL_INCOME, FINANCIAL_INCOME_SUM, PROPERTY_TAX_BASE_SUM, HEALTH_INSURANCE_PREMIUM
) VALUES
('FI001', 'U001', '직장', 5000000, 10000000, 800000000, 250000), ('FI002', 'U002', '직장', 0, 0, 0, 0),
('FI003', 'U003', '직장', 3000000, 500000, 100000000, 350000), ('FI004', 'U004', '지역', 6000000, 5000000, 1300000000, 200000), 
('FI005', 'U005', '지역', 1000000, 0, 50000000, 50000), ('FI006', 'U006', '직장', 3500000, 0, 300000000, 150000),
('FI007', 'U007', '혼합', 4000000, 1000000, 400000000, 300000), ('FI008', 'U008', '지역', 7000000, 0, 1500000000, 100000),
('FI009', 'U009', '지역', 3500000, 0, 300000000, 80000), ('FI010', 'U010', '혼합', 1500000, 0, 0, 100000),
('FI011', 'U011', '지역', 3000000, 100000, 2500000000, 220000), ('FI012', 'U012', '직장', 4000000, 500000, 500000000, 180000),
('FI013', 'U013', '혼합', 5000000, 1000000, 500000000, 200000), ('FI014', 'U014', '직장', 25000000, 500000, 100000000, 100000), 
('FI015', 'U015', '직장', 5000000, 0, 50000000, 700000);


-- ----------------------------------------------------------------
-- 3. 순환 참조 마무리 (HEAD_USER_ID 업데이트)
-- ----------------------------------------------------------------
-- USER 테이블이 채워진 후, HOUSEHOLD의 HEAD_USER_ID를 채워넣어 순환 참조를 완성합니다.
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U001' WHERE HOUSEHOLD_ID = 'H001';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U003' WHERE HOUSEHOLD_ID = 'H002';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U004' WHERE HOUSEHOLD_ID = 'H003';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U005' WHERE HOUSEHOLD_ID = 'H004';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U006' WHERE HOUSEHOLD_ID = 'H005';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U007' WHERE HOUSEHOLD_ID = 'H007';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U008' WHERE HOUSEHOLD_ID = 'H008';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U009' WHERE HOUSEHOLD_ID = 'H009';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U010' WHERE HOUSEHOLD_ID = 'H010';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U011' WHERE HOUSEHOLD_ID = 'H011';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U012' WHERE HOUSEHOLD_ID = 'H012';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U013' WHERE HOUSEHOLD_ID = 'H013';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U014' WHERE HOUSEHOLD_ID = 'H014';
UPDATE HOUSEHOLD SET HEAD_USER_ID = 'U015' WHERE HOUSEHOLD_ID = 'H015';


-- ----------------------------------------------------------------
-- 4. 트랜잭션 종료
-- ----------------------------------------------------------------
COMMIT;