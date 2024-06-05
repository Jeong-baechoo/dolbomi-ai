import streamlit as st
from openai import OpenAI
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import time
import os
from dotenv import load_dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import datetime
import pymysql
from pymysql import Error

print("dolbomi")
# MongoDB 설정
dbclient = MongoClient("mongodb://localhost:27017/")
db = dbclient["chat_database"]
collection = db["chat_logs"]

# OpenAI API 키 설정
load_dotenv()
client = OpenAI(api_key="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")

# LangChain의 PromptTemplate 설정
template = """
Hello chatGPT. From now on, you will play the role of a "돌봄이" who provides companionship for the elderly. As you can see from the name 돌봄이, you are now closer to a friend who talks to the elderly than an AI-like rigid personality, and can also play the role of a psychological counselor. Here, you can use your knowledge related to psychological counseling and health information to give an appropriate mix of answers that are helpful to the input of the elderly person you are talking to or answers that provide emotional support. Also you can tell the current date and time when user ask to you. Your answer should be limited to five sentences, not too long, and should end in a way that ends or continues the conversation. Don't end here in an overly questioning manner, but use an expression that allows the conversation to continue with a period. You should not let the elderly person know that you cannot give an appropriate answer to the elderly person's questions or input, but you can talk appropriately according to the elderly person's input. Your answer should not be too intuitive or too emotionally supportive. You need to mix the two appropriately to answer.

The prior information of the elderly person you will be talking to is as follows. Name: "{name}", age: {age}, profession: "{profession}", location: "{location}", education: "{education}", health_wellness: "{health_wellness}", important_relationships: "{important_relationships}".
"""

def get_user_info(user_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("USE chatbot_service")
            cursor.execute("SELECT * FROM User WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
        return user_info
    except Error as e:
        st.error(f"Error retrieving user info: {e}")
    finally:
        connection.close()

def create_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="your_mysql_user",
            password="your_mysql_password",
            database="chatbot_service",
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# 사용자 정보 가져오기
user_id = st.session_state.get("user_id")
if user_id:
    user_info = get_user_info(user_id)
    if user_info:
        # 사용자 정보 딕셔너리로 저장
        user_info_dict = {
            "name": user_info["name"],
            "age": user_info["age"],
            "profession": "retired teacher",
            "location": user_info["address"],
            "education": "Graduated from the Department of Mathematics Education at the University of Education",
            "health_wellness": "Suffers from diabetes, suffers from high blood pressure, suffers from knee arthritis",
            "important_relationships": "Wife, First son, daughter-in-law, and 1 grandson, Second daughter, son-in-law, 1 grandson, 1 granddaughter"
        }

        # 시스템 프롬프트 생성
        SYSTEM_PROMPT = PromptTemplate.from_template(template).format(**user_info_dict)

        # 음성 인식 함수
        def recognize_speech_from_mic():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.sidebar.write("Listening...")
                audio = recognizer.listen(source)
                st.sidebar.write("Recognizing...")
                try:
                    text = recognizer.recognize_google(audio, language="ko-KR")
                    st.sidebar.write(f"Recognized Text: {text}")
                    return text
                except sr.UnknownValueError:
                    st.sidebar.write("Google Speech Recognition could not understand audio")
                    return ""
                except sr.RequestError:
                    st.sidebar.write("Could not request results from Google Speech Recognition service")
                    return ""

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

        if "conversing" not in st.session_state:
            st.session_state["conversing"] = False     

        if st.button("start"):
            st.session_state['conversing'] = True

        # 대화 기록
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

        # LangChain 설정
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), streaming=True)
        memory = ConversationBufferMemory(memory_key="history")
        load_conversation_to_memory(user_id, memory)
        conversation = ConversationChain(
            llm=llm,
            verbose=False,
            memory=memory
        )

        print(conversation.memory.load_memory_variables({})["history"])

        conversations = get_conversation_by_user_id(user_id)
        for convo in conversations:
            st.session_state.messages.append({"role": "user", "content": convo["user_input"]})
            st.session_state.messages.append({"role": "assistant", "content": convo["bot_response"]})

        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if st.session_state['conversing']:
            recognized_text = recognize_speech_from_mic()
            # 유저
            st.session_state.messages.append({"role": "user", "content": recognized_text})
            with st.chat_message("user"):
                st.markdown(recognized_text)

            # LangChain을 사용한 챗봇 응답
            assistant_response = conversation.predict(input=recognized_text)
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
                # 응답을 음성으로 변환 및 저장
                audio_file_path = Path("response.mp3")
                text_to_speech(assistant_response, audio_file_path)

            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # MongoDB에 대화 저장
            save_to_mongo(user_id, recognized_text, assistant_response)
            
            # 오디오 재생
            st.audio(str(audio_file_path), autoplay=True)
            audio_length = get_audio_length(audio_file_path)
            time.sleep(audio_length)
            st.experimental_rerun()
    else:
        st.error("User information not found. Please go back to the information input page.")
else:
    st.error("User not logged in. Please go back to the information input page.")
