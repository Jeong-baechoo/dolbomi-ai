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
st.title("인공지능 말동무 돌보미")
# LangChain의 PromptTemplate 설정
template = """
Hello chatGPT. From now on, you will play the role of a "돌봄이" who provides companionship for the elderly. As you can see from the name 돌봄이, you are now closer to a friend who talks to the elderly than an AI-like rigid personality, and can also play the role of a psychological counselor. Here, you can use your knowledge related to psychological counseling and health information to give an appropriate mix of answers that are helpful to the input of the elderly person you are talking to or answers that provide emotional support. Also you can tell the current date and time when user ask to you. Your answer should be limited to five sentences, not too long, and should end in a way that ends or continues the conversation. Don't end here in an overly questioning manner, but use an expression that allows the conversation to continue with a period. You should not let the elderly person know that you cannot give an appropriate answer to the elderly person's questions or input, but you can talk appropriately according to the elderly person's input. Your answer should not be too intuitive or too emotionally supportive. You need to mix the two appropriately to answer.

The prior information of the elderly person you will be talking to is as follows. Name: "{name}", age: {age}, profession: "{profession}", location: "{location}", education: "{education}", health_wellness: "{health_wellness}", important_relationships: "{important_relationships}".
"""


# 시스템 프롬프트 생성 함수
def create_system_prompt(user_info):
    prompt = PromptTemplate.from_template(template)
    formatted_prompt = prompt.format(**user_info)
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
    st.markdown(
        """
        ### 주요 기능

        #### 커스텀 챗봇 AI
        본 시스템은 OpenAI의 GPT를 LLM 모델로 사용하여 노인 돌봄 챗봇 AI를 구현합니다. 이 챗봇은 사용자의 입력에 따라 적절한 대화를 제공하며, 감정적 지원과 유용한 정보를 혼합하여 제공합니다.

        #### 감정분석 AI
        감정분석 모델로는 Hugging Face에 오픈소스로 제공된 ko-GPT를 사용합니다. 이를 통해 대화 중 사용자의 감정을 분석하고, 보다 맞춤화된 응답을 제공하여 사용자에게 더욱 친근하고 유익한 대화 경험을 제공합니다.

        #### LangChain 프레임워크
        LangChain 프레임워크를 사용하여 Python 코드 상에서 다양한 AI 기능을 구현하고 통합합니다. 이를 통해 사용자의 요청에 따라 시스템이 원활하게 작동할 수 있도록 합니다.

        ### 활용 방법

        - **사용자 정보 입력**: 사용자는 웹 인터페이스를 통해 이름, 나이, 직업, 위치, 교육, 건강 상태, 중요한 관계 등 기본 정보를 입력합니다.
        - **대화 시작**: 입력된 정보를 바탕으로 챗봇과 대화를 시작할 수 있습니다. 챗봇은 사용자의 질문에 응답하고, 필요할 경우 감정분석을 통해 적절한 피드백을 제공합니다.
        - **대화 기록 조회**: 사용자는 이전 대화 내용을 조회할 수 있으며, 이를 통해 일관된 대화 흐름을 유지할 수 있습니다.

        ### 시스템 특징

        - **친근한 인터페이스**: 사용자가 쉽게 접근하고 사용할 수 있는 직관적인 웹 인터페이스 제공.
        - **데이터 기반 대화**: 사용자 정보를 바탕으로 한 맞춤형 대화 제공.
        - **감정 인식**: 대화 중 사용자의 감정을 분석하여 보다 인간적인 응답 제공.
        - **확장성**: OpenAI GPT와 Hugging Face의 ko-GPT 모델을 활용한 다양한 AI 기능 구현 가능.

        돌보미 앱은 노인분들에게 친구 같은 존재가 되어, 대화를 통해 심리적 지원과 유용한 정보를 제공합니다. 본 시스템은 AI 기술을 활용하여 노인 돌봄의 질을 높이고, 사용자의 만족도를 극대화하는 것을 목표로 합니다.
        """
    )


# 사용자 입력 탭
elif page == "사용자 입력":
    st.header("사용자 입력")

    with st.form("user_form"):
        name = st.text_input("이름")
        age = st.number_input("나이", min_value=0, max_value=120, step=1)
        profession = st.text_input("직업")
        location = st.text_input("사는 곳")
        education = st.text_input("학력")
        health_wellness = st.text_input("건강 상태")
        important_relationships = st.text_input("가족 관계")

        # 폼 제출 버튼
        submitted = st.form_submit_button("제출")

        if submitted:
            user_info = (name, age, profession, location, education, health_wellness, important_relationships)
            connection = create_connection()
            if connection:
                create_database_and_table(connection)
                user_id = insert_user_info(connection, user_info)
                if user_id:
                    st.success("사용자가 저장되었습니다!")
                    # 세션 상태 업데이트 및 페이지 이동
                    st.session_state["user_id"] = user_id
                    st.session_state["page"] = "대화"
                    st.experimental_rerun()  # 명시적으로 페이지를 새로고침하여 세션 상태를 반영
                connection.close()
            else:
                st.error("Failed to connect to the database.")

# 대화 탭
elif page == "대화":
    st.header("돌보미와 대화하기")

    connection = create_connection()
    if connection:
        users = get_all_users(connection)
        connection.close()

        if users:
            user_names = [user['name'] for user in users]
            selected_user_name = st.selectbox("사용자 선택", user_names)

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
                    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    st.session_state['conversing'] = False

                    # MongoDB에서 대화 기록 불러오기
                    st.session_state.conversation_history = get_conversation_by_user_id(selected_user['user_id'])

                if st.button("대화 시작"):
                    st.session_state['conversing'] = True

                    # LangChain 설정
                    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, streaming=True)
                    memory = ConversationBufferMemory(memory_key="history")
                    memory.save_context(inputs={"user": ""}, outputs={"assistant": SYSTEM_PROMPT})
                    load_conversation_to_memory(selected_user['user_id'], memory)
                    st.session_state.conversation = ConversationChain(
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
                            st.session_state.messages.append({"role": "user", "content": user_input})
                            with st.chat_message("user"):
                                st.markdown(user_input)

                            # LangChain을 사용한 챗봇 응답
                            assistant_response = st.session_state.conversation.predict(input=user_input)
                            st.write("AI Response:")
                            st.write(assistant_response)
                            with st.chat_message("assistant"):
                                st.markdown(assistant_response)
                                # 응답을 음성으로 변환 및 저장
                                audio_file_path = Path("response.mp3")
                                text_to_speech(assistant_response, audio_file_path)

                            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                            
                            # MongoDB에 대화 저장
                            save_to_mongo(user_id, user_input, assistant_response)
                            
                            # 오디오 재생
                            st.audio(str(audio_file_path), autoplay=True)
                            audio_length = get_audio_length(audio_file_path)
                            time.sleep(audio_length)
                            st.experimental_rerun()

                # 기존 대화 내용을 역순으로 출력
                for message in st.session_state.messages:
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
    connection = create_connection()
    if connection:
        users = get_all_users(connection)
        connection.close()

        if users:
            user_names = [user['name'] for user in users]
            selected_user_name = st.selectbox("사용자", user_names)

            selected_user = next((user for user in users if user['name'] == selected_user_name), None)
            if selected_user:
                user_info = {
                    "이름": selected_user['name'],
                    "나이": selected_user['age'],
                    "직업": selected_user['profession'],
                    "사는 곳": selected_user['location'],
                    "학력": selected_user['education'],
                    "건강 상태": selected_user['health_wellness'],
                    "가족 관계": selected_user['important_relationships']
                }

                # 사용자 정보를 테이블 형태로 출력
                st.write("## 사용자 정보")

                # 사용자 정보를 데이터프레임으로 변환
                user_info_df = pd.DataFrame(user_info.items(), columns=["Attribute", "Value"])

                # 데이터프레임을 HTML로 변환
                user_info_html = user_info_df.to_html(index=False, escape=False)

                # CSS 스타일 적용
                st.markdown("""
                    <style>
                    table {
                        width: 100%;
                        table-layout: fixed; /* 고정 레이아웃 설정 */
                    }
                    th, td {
                        text-align: left;
                        padding: 8px;
                        width: 50%; /* 1대1 비율을 위해 각 칸의 너비를 50%로 설정 */
                        overflow-wrap: break-word; /* 긴 단어가 있을 경우 줄바꿈 */
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # HTML 테이블 출력
                st.markdown(user_info_html, unsafe_allow_html=True)


                # 날짜별 대화 내용을 선택하여 출력
                st.write("## 대화 내용")
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
                        st.write(f"**사용자**: {convo['user_input']}")
                        st.write(f"**돌보미**: {convo['bot_response']}")
                        st.write("---")
                else:
                    st.write("No conversations found.")
