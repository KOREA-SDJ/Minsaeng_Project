CREATE VIEW V_FINAL_REPORT AS
SELECT
    D.DETERM_ID AS 판정_번호,
    U.USER_ID AS 사용자_ID,
    U.NAME AS 신청자_이름,
    H.MEMBER_COUNT AS 가구원_수,
    
    -- 판정 결과 코드 변환 (Y/N -> 한글)
    CASE D.BENEFIT_STATUS
        WHEN 'Y' THEN '지급 대상'
        ELSE '탈락'
    END AS 판정_결과,
    
    D.SCHEDULED_PAYMENT AS 지급_예정액,
    
    -- 탈락 사유 상세 설명 연결
    IFNULL(RR.REASON_DESCRIPTION, '-(해당 없음)') AS 탈락_사유_상세

FROM 
    DETERMINATION D
JOIN 
    USER U ON D.USER_ID = U.USER_ID
JOIN 
    HOUSEHOLD H ON U.HOUSEHOLD_ID = H.HOUSEHOLD_ID
LEFT JOIN 
    REJECTION_REASON RR ON D.REASON_CODE = RR.REASON_CODE;