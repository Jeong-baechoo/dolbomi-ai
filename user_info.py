import streamlit as st
import pymysql
from pymysql import Error

# MySQL 연결 설정
def create_connection():
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="1234",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# 데이터베이스와 테이블 생성
def create_database_and_table(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS chatbot_service")
            cursor.execute("USE chatbot_service")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS User (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                profession VARCHAR(100),
                location VARCHAR(255),
                education VARCHAR(255),
                health_wellness VARCHAR(255),
                important_relationships VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        connection.commit()
    except Error as e:
        st.error(f"Error creating database or table: {e}")

def insert_user_info(connection, user_info):
    try:
        with connection.cursor() as cursor:
            cursor.execute("USE chatbot_service")
            insert_query = """
            INSERT INTO User (name, age, profession, location, education, health_wellness, important_relationships)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, user_info)
            connection.commit()
            return cursor.lastrowid
    except Error as e:
        st.error(f"Error inserting user info: {e}")

st.title("User Information Input")

# 사용자 입력 폼
with st.form("유저 정보"):
    name = st.text_input("이름")
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    profession = st.text_input("직업")
    location = st.text_input("지역")
    education = st.text_input("학력")
    health_wellness = st.text_input("질병 정보")
    important_relationships = st.text_input("가족 및 친구 관계")

    # 폼 제출 버튼
    submitted = st.form_submit_button("제출")

    if submitted:
        user_info = (name, age, profession, location, education, health_wellness, important_relationships)
        connection = create_connection()
        if connection:
            create_database_and_table(connection)
            user_id = insert_user_info(connection, user_info)
            if user_id:
                st.success("User information saved successfully!")
                # 세션 상태 업데이트 및 페이지 이동
                st.session_state["user_id"] = user_id
                st.session_state["page"] = "chat"
                st.experimental_rerun()
            connection.close()
        else:
            st.error("Failed to connect to the database.")
