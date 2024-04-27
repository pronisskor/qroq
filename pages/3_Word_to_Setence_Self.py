from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import streamlit as st
import pandas as pd
import random

# Streamlit 페이지 타이틀 설정
st.title("🦜🔗 Word to Sentence")

# 환경 변수에서 API 키 불러오기
groq_api_key = st.secrets["GROQ_API_KEY"]

# Groq Langchain 챗 객체 초기화
groq_chat = ChatGroq(api_key=groq_api_key, model_name="gemma-7b-it")

# 대화 메모리 설정
memory = ConversationBufferWindowMemory(k=5)

# 대화 체인 설정
conversation = ConversationChain(llm=groq_chat, memory=memory)

# 파일 업로더 설정
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

def load_words(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file)
    else:
        st.error("Unsupported file type.")
        return []

    if 'words' in df.columns:
        return df['words'].dropna().tolist()
    else:
        st.error("No 'words' column found in the file.")
        return []

if uploaded_file is not None:
    if 'words_list' not in st.session_state or st.button("Restart"):
        words_list = load_words(uploaded_file)
        st.session_state['words_list'] = words_list
        st.session_state['learned_count'] = 0

def generate_sentence(word):
    try:
        response = conversation.run([
            {"role": "system", "content": "When an English word is provided, you need to create one simple and easy English conversation sentence that is commonly used in everyday life. You also need to provide one Korean translation of the English conversation sentence you created. In this way, you should provide a total of only two sentences."},
            {"role": "user", "content": word}
        ])
        return response
    except Exception as e:
        st.error(f"Error during API call: {e}")
        return None

if 'words_list' in st.session_state and st.session_state['words_list']:
    word = st.session_state['words_list'].pop(0)
    sentence = generate_sentence(word)
    if sentence:
        st.write(f"Generated sentence for '{word}': {sentence}")
    st.session_state['learned_count'] += 1
    st.write(f"Processed words count: {st.session_state['learned_count']}")

    if st.session_state['words_list']:
        st.button("Next Word")
    else:
        st.write("All words have been processed.")
