import openai
import mysql.connector
import json
import csv

# OpenAI API 키 설정
openai.api_key = ""

# MySQL 데이터베이스 설정
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "NLP_user",
    "password": "NLP_password",
    "database": "NLP_db"
}

def generate_skill_info(skill_name):
    prompt = f"""
    스킬 이름: {skill_name}
    JSON 형식으로 다음과 같이 응답해 주세요:
    {{
        "스킬 이름": "{skill_name}",
        "목차": [
            {{
                "목차 제목": "첫 번째 목차 제목",
                "학습내용": ["내용1", "내용2", "내용3"]
            }},
            {{
                "목차 제목": "두 번째 목차 제목",
                "학습내용": ["내용1", "내용2", "내용3"]
            }},
            {{
                "목차 제목": "세 번째 목차 제목",
                "학습내용": ["내용1", "내용2", "내용3"]
            }},
            {{
                "목차 제목": "네 번째 목차 제목",
                "학습내용": ["내용1", "내용2", "내용3"]
            }},
            {{
                "목차 제목": "다섯 번째 목차 제목",
                "학습내용": ["내용1", "내용2", "내용3"]
            }}
        ]
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    try:
        skill_info = json.loads(response.choices[0].message["content"])
        return skill_info
    except json.JSONDecodeError:
        print("응답이 JSON 형식이 아닙니다.")
        return None

def save_skill_info_to_csv(skill_info, skill_id):
    with open("skill_data.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # CSV 파일에 첫 번째 줄에 헤더 작성 (한번만 실행되도록 설정)
        if file.tell() == 0:
            writer.writerow(["msinfo1", "msinfo2", "msinfo3", "msname", "ms_csid_csid"])

        # 스킬 정보를 CSV 파일에 작성
        for chapter in skill_info["목차"]:
            msname = chapter["목차 제목"]  # 각 목차 제목을 msname에 할당
            msinfo1 = chapter["학습내용"][0] if len(chapter["학습내용"]) > 0 else None
            msinfo2 = chapter["학습내용"][1] if len(chapter["학습내용"]) > 1 else None
            msinfo3 = chapter["학습내용"][2] if len(chapter["학습내용"]) > 2 else None
            writer.writerow([msinfo1, msinfo2, msinfo3, msname, skill_id])
            
def insert_mastery_skill_data(skill_info, skill_id, db_connection):
    cursor = db_connection.cursor()
    query = """
        INSERT INTO mastery_skil (msinfo1, msinfo2, msinfo3, msname, mscsid_csid)
        VALUES (%s, %s, %s, %s, %s)
    """
    for chapter in skill_info["목차"]:
        msname = chapter["목차 제목"]
        msinfo1 = chapter["학습내용"][0] if len(chapter["학습내용"]) > 0 else None
        msinfo2 = chapter["학습내용"][1] if len(chapter["학습내용"]) > 1 else None
        msinfo3 = chapter["학습내용"][2] if len(chapter["학습내용"]) > 2 else None

        cursor.execute(query, (msinfo1, msinfo2, msinfo3, msname, skill_id))
    db_connection.commit()
    cursor.close()

# 스킬 목록
skill_names = ["Cordova", "SwiftTesting", "SQLite", "Room","Espresso"]  # 여기에 스킬을 추가

# DB 연결
db_connection = mysql.connector.connect(**db_config)

# 스킬 데이터를 반복하여 CSV 파일로 저장하고, DB에 삽입
skill_id = 178  # 첫 스킬의 ID는 1부터 시작
for skill_name in skill_names:
    skill_info = generate_skill_info(skill_name)
    if skill_info:
        save_skill_info_to_csv(skill_info, skill_id)  # CSV 파일에 저장
        insert_mastery_skill_data(skill_info, skill_id, db_connection)  # DB 삽입
        skill_id += 1  # 다음 스킬에 대해 ID를 증가
    else:
        print(f"{skill_name}에 대한 유효한 JSON 응답을 받지 못했습니다.")

# DB 연결 종료
db_connection.close()