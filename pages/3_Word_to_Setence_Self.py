from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import streamlit as st
import os
import pandas as pd
import random
from groq import Groq
import json

# Streamlit 페이지 타이틀 설정
st.title("🦜🔗 Word to Sentence")

# 환경 변수에서 API 키 불러오기
groq_api_key = st.secrets["GROQ_API_KEY"]

# Groq Langchain 챗 객체 초기화
groq_chat = ChatGroq(api_key=groq_api_key, model_name="llama3-8b-8192")

# 대화 메모리 설정
memory = ConversationBufferWindowMemory(k=5)

# 대화 체인 설정
conversation = ConversationChain(
    llm=groq_chat,
    memory=memory
)

# 파일 업로더 설정
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
if uploaded_file is not None:
    if st.button("Restart"):
        if 'words_list' in st.session_state:
            del st.session_state['words_list']
        st.session_state['learned_count'] = 0  # 학습 카운터 초기화

if 'words_list' not in st.session_state:
    st.session_state['words_list'] = []
    st.session_state['learned_count'] = 0  # 학습 카운터를 세션 상태에 추가

if uploaded_file is not None and not st.session_state['words_list']:
    def load_file(uploaded_file):
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            return pd.read_excel(uploaded_file)

    df = load_file(uploaded_file)
    words_column = 'words'
    if df is not None and words_column in df.columns:
        st.session_state['words_list'] = df[words_column].dropna().tolist()
        random.shuffle(st.session_state['words_list'])

def load_messages():
    file_path = os.path.join(os.getcwd(), "pages", "messages.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            messages = json.load(file)
        return messages
    else:
        raise FileNotFoundError("messages.json 파일을 찾을 수 없습니다.")

def generate_sentence_with_word(word):
    print(f"Generating sentence for word: {word}")  # 단어 확인 로그 추가
    messages = load_messages()

    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        print("API response received")  # API 응답 로그
        response = completion.choices[0].message.content
        print(f"Response content: {response}")  # 응답 내용 로그

        lines = response.split('\n')
        english_sentence, korean_translation = None, None
        for line in lines:
            cleaned_line = line.strip().strip('"')
            if '**English:**' in cleaned_line:
                english_sentence = cleaned_line.replace('**English:**', '').strip().strip('"')
            elif '**Korean:**' in cleaned_line:
                korean_translation = cleaned_line.replace('**Korean:**', '').strip().strip('"')

        if english_sentence and korean_translation:
            return english_sentence, korean_translation
        else:
            raise ValueError("Response does not contain expected format of English and Korean sentences.")
    except Exception as e:
        print(f"API 호출 중 오류가 발생했습니다: {e}")  # 오류 상세 로그
        return None, None


if st.session_state.get('words_list'):
    random_word = st.session_state['words_list'].pop(0)
    st.session_state['learned_count'] += 1
    with st.spinner('문장 생성중...'):
        english_sentence, korean_translation = generate_sentence_with_word(random_word)
        if english_sentence and korean_translation:
            highlighted_english_sentence = english_sentence.replace(random_word, f'<strong>{random_word}</strong>')
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{highlighted_english_sentence}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{korean_translation}</p>', unsafe_allow_html=True)
            st.markdown(f'공부한 단어 수: {st.session_state["learned_count"]}')

if uploaded_file is not None and 'words_list' in st.session_state:
    if st.button("다음 단어"):
        if not st.session_state['words_list']:
            st.markown(f'<p style="background-color: #bffff2; padding: 10px;">모든 단어에 대한 문장을 생성했습니다.</p>', unsafe_allow_html=True)
            del st.session_state['words_list']
            st.session_state['learned_count'] = 0  # 학습 카운터 초기화
