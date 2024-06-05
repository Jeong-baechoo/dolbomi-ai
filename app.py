import streamlit as st
import importlib


# 페이지 초기화
if "page" not in st.session_state:
    st.session_state["page"] = "personal_info"

# 페이지 라우팅
if st.session_state["page"] == "personal_info":
    personal_info = importlib.import_module("user_info")
    personal_info
elif st.session_state["page"] == "chat":
    chat_page = importlib.import_module("dolbomi_ai")
    chat_page
