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
            cursor.execute("CREATE DATABASE IF NOT EXISTS user_info")
            cursor.execute("USE user_info")
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
            cursor.execute("USE user_info")
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
with st.form("user_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    profession = st.text_input("Profession")
    location = st.text_input("Location")
    education = st.text_input("Education")
    health_wellness = st.text_input("Health Wellness")
    important_relationships = st.text_input("Important Relationships")

    # 폼 제출 버튼
    submitted = st.form_submit_button("Submit")

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
                st.experimental_rerun()  # 명시적으로 페이지를 새로고침하여 세션 상태를 반영
            connection.close()
        else:
            st.error("Failed to connect to the database.")
