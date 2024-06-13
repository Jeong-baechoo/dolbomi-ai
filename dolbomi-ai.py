import streamlit as st
import pymysql
from pymysql import Error
from openai import OpenAI
from pathlib import Path
import time
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

def get_all_users(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("USE user_info")
            cursor.execute("SELECT * FROM User")
            return cursor.fetchall()
    except Error as e:
        st.error(f"Error retrieving user info: {e}")
        return []

# MongoDB 설정
dbclient = MongoClient("mongodb://localhost:27017/")
db = dbclient["chat_database"]
collection = db["chat_logs"]

client = OpenAI(api_key=OPENAI_API_KEY)
st.title("ChatGPT-like clone")

# LangChain의 PromptTemplate 설정
template = """
Hello chatGPT. From now on, you will play the role of a "돌봄이" who provides companionship for the elderly. As you can see from the name 돌봄이, you are now closer to a friend who talks to the elderly than an AI-like rigid personality, and can also play the role of a psychological counselor. Here, you can use your knowledge related to psychological counseling and health information to give an appropriate mix of answers that are helpful to the input of the elderly person you are talking to or answers that provide emotional support. Also you can tell the current date and time when user ask to you. Your answer should be limited to five sentences, not too long, and should end in a way that ends or continues the conversation. Don't end here in an overly questioning manner, but use an expression that allows the conversation to continue with a period. You should not let the elderly person know that you cannot give an appropriate answer to the elderly person's questions or input, but you can talk appropriately according to the elderly person's input. Your answer should not be too intuitive or too emotionally supportive. You need to mix the two appropriately to answer.

The prior information of the elderly person you will be talking to is as follows. Name: "{name}", age: {age}, profession: "{profession}", location: "{location}", education: "{education}", health_wellness: "{health_wellness}", important_relationships: "{important_relationships}".
"""

# 시스템 프롬프트 생성 함수
def create_system_prompt(user_info):
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(**user_info)
    st.write("Generated Prompt:")
    st.write(formatted_prompt)
    return formatted_prompt

# 텍스트를 음성으로 변환하는 함수
def text_to_speech(text, file_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    response.stream_to_file(file_path)

def get_audio_length(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000  # 밀리초를 초로 변환

def save_to_mongo(user_id, user_input, bot_response):
    document = {
        "user_id": user_id,
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response
    }
    collection.insert_one(document)

def get_conversation_by_user_id(user_id):
    return list(collection.find({"user_id": user_id}).sort("timestamp", -1))

def load_conversation_to_memory(user_id, memory):
    conversations = get_conversation_by_user_id(user_id)
    for convo in conversations:
        memory.save_context(inputs={"user": convo["user_input"]}, outputs={"assistant": convo["bot_response"]})

# 탭 설정
tabs = ["돌보미 앱 소개", "사용자 입력", "대화", "사용자 정보와 대화 내용"]
page = st.sidebar.selectbox("Choose a page", tabs)

# 돌보미 앱 소개
if page == "돌보미 앱 소개":
    st.write("# 돌보미 앱 소개")
    st.markdown(
        """
        돌보미 앱은 노인분들을 위해 개발된 챗봇입니다.
        이 챗봇은 친구처럼 대화를 나누고 심리 상담을 제공할 수 있습니다.
        현재 날짜와 시간을 알려줄 수 있으며, 건강 정보와 관련된 조언도 제공합니다.
        대화는 적절한 감정 지원과 정보를 혼합하여 제공합니다.
        """
    )

# 사용자 입력 탭
elif page == "사용자 입력":
    st.header("User Information Input")

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
                    st.session_state["page"] = "대화"
                    st.experimental_rerun()  # 명시적으로 페이지를 새로고침하여 세션 상태를 반영
                connection.close()
            else:
                st.error("Failed to connect to the database.")

# 대화 탭
elif page == "대화":
    st.header("Chat with 돌봄이")

    connection = create_connection()
    if connection:
        users = get_all_users(connection)
        connection.close()

        if users:
            user_names = [user['name'] for user in users]
            selected_user_name = st.selectbox("Select User", user_names)

            selected_user = next((user for user in users if user['name'] == selected_user_name), None)
            if selected_user:
                user_info = {
                    "name": selected_user['name'],
                    "age": selected_user['age'],
                    "profession": selected_user['profession'],
                    "location": selected_user['location'],
                    "education": selected_user['education'],
                    "health_wellness": selected_user['health_wellness'],
                    "important_relationships": selected_user['important_relationships']
                }
                SYSTEM_PROMPT = create_system_prompt(user_info)

                if "conversing" not in st.session_state:
                    st.session_state["conversing"] = False     

                # 새로운 사용자를 선택했을 때 메시지 초기화 및 대화 기록 불러오기
                if "selected_user" not in st.session_state or st.session_state.selected_user != selected_user_name:
                    st.session_state.selected_user = selected_user_name
                    st.session_state.messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]
                    st.session_state['conversing'] = False

                    # MongoDB에서 대화 기록 불러오기
                    st.session_state.conversation_history = get_conversation_by_user_id(selected_user['user_id'])

                if st.button("Start Conversation"):
                    st.session_state['conversing'] = True

                # LangChain 설정
                llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, streaming=True)
                memory = ConversationBufferMemory(memory_key="history")
                load_conversation_to_memory(selected_user['user_id'], memory)
                conversation = ConversationChain(
                    llm=llm,
                    verbose=False,
                    memory=memory
                )

                if st.session_state['conversing']:
                    user_id = selected_user['user_id']
                    user_input = st.text_input("Enter your message:")
                    if st.button("Send"):
                        if user_input:
                            # 유저
                            st.session_state.messages.insert(0, {"role": "user", "content": user_input})
                            with st.chat_message("user"):
                                st.markdown(user_input)

                            # LangChain을 사용한 챗봇 응답
                            assistant_response = conversation.predict(input=user_input)
                            st.write("AI Response:")
                            st.write(assistant_response)
                            with st.chat_message("assistant"):
                                st.markdown(assistant_response)
                                # 응답을 음성으로 변환 및 저장
                                audio_file_path = Path("response.mp3")
                                text_to_speech(assistant_response, audio_file_path)

                            st.session_state.messages.insert(0, {"role": "assistant", "content": assistant_response})
                            
                            # MongoDB에 대화 저장
                            save_to_mongo(user_id, user_input, assistant_response)
                            
                            # 오디오 재생
                            st.audio(str(audio_file_path), autoplay=True)
                            audio_length = get_audio_length(audio_file_path)
                            time.sleep(audio_length)
                            st.experimental_rerun()

                # 기존 대화 내용을 역순으로 출력
                for message in reversed(st.session_state.messages):
                    if message["role"] != "system":
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                # MongoDB에서 불러온 대화 기록을 출력
                for convo in st.session_state.conversation_history:
                    with st.chat_message("user"):
                        st.markdown(convo["user_input"])
                    with st.chat_message("assistant"):
                        st.markdown(convo["bot_response"])

# 사용자 정보와 대화 내용 탭
elif page == "사용자 정보와 대화 내용":
    st.header("User Information and Conversations")

    connection = create_connection()
    if connection:
        users = get_all_users(connection)
        connection.close()

        if users:
            user_names = [user['name'] for user in users]
            selected_user_name = st.selectbox("Select User", user_names)

            selected_user = next((user for user in users if user['name'] == selected_user_name), None)
            if selected_user:
                user_info = {
                    "name": selected_user['name'],
                    "age": selected_user['age'],
                    "profession": selected_user['profession'],
                    "location": selected_user['location'],
                    "education": selected_user['education'],
                    "health_wellness": selected_user['health_wellness'],
                    "important_relationships": selected_user['important_relationships']
                }

                # 사용자 정보를 테이블 형태로 출력
                st.write("## 사용자 정보")
                user_info_df = pd.DataFrame(user_info.items(), columns=["Attribute", "Value"])
                st.dataframe(user_info_df)

                # 날짜별 대화 내용을 선택하여 출력
                st.write("## MongoDB 대화 내용")
                user_id = selected_user['user_id']
                mongo_conversations = get_conversation_by_user_id(user_id)
                
                if mongo_conversations:
                    # 대화 기록에서 날짜 추출
                    dates = sorted(list(set([convo["timestamp"].date() for convo in mongo_conversations])))
                    
                    # 최신 날짜를 기본값으로 설정
                    selected_date = st.selectbox("날짜 선택", dates, index=len(dates)-1)
                    
                    # 선택한 날짜의 대화만 필터링
                    selected_conversations = [convo for convo in mongo_conversations if convo["timestamp"].date() == selected_date]
                    
                    for convo in selected_conversations:
                        st.write(f"**시간**: {convo['timestamp'].time()}")
                        st.write(f"**User**: {convo['user_input']}")
                        st.write(f"**Bot**: {convo['bot_response']}")
                        st.write("---")
                else:
                    st.write("No conversations found.")
