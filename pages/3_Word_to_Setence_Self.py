from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import streamlit as st
import os
import pandas as pd
import random
from groq import Groq

# Streamlit 페이지 타이틀 설정
st.title("🦜🔗 Word to Sentence")

# 환경 변수에서 API 키 불러오기
groq_api_key = st.secrets["GROQ_API_KEY"]

# Groq Langchain 챗 객체 초기화
groq_chat = ChatGroq(api_key=groq_api_key, model_name="gemma-7b-it")

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

def generate_sentence_with_word(word):
    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="gemma-7b-it",
            messages=[
                {
                    "role": "system",
                    "content": "When an English word is provided, you need to create one simple and easy English conversation sentence that is commonly used in everyday life using the word '{}'. You also need to provide one Korean translation of the English conversation sentence you created. In this way, you should provide a total of only two sentences.".format(word)
                },
                {
                    "role": "user",
                    "content": "Create a sentence using '{}'.".format(word)
                }
            ],
            temperature=0,
            max_tokens=1024,
            top_p=0,
            stream=False
        )
        response = completion.choices[0].message.content
        parts = response.split('\n')
        # 영어 문장과 한국어 번역을 찾기 위해 각 줄을 검사합니다.
        english_sentence, korean_translation = None, None
        for part in parts:
            clean_part = part.strip().strip('"')  # 양쪽 공백과 따옴표 제거
            if clean_part.endswith('"'):  # 마지막 따옴표 제거
                clean_part = clean_part[:-1].strip()
            if '**English:**' in part:
                english_sentence = clean_part.replace('**English:**', '').strip()
            elif '**Korean:**' in part:
                korean_translation = clean_part.replace('**Korean:**', '').strip()

        if english_sentence and korean_translation:
            return english_sentence, korean_translation
        else:
            raise ValueError("Response does not contain expected format of English and Korean sentences.")
    except Exception as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {e}")
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
            st.markdown(f'<p style="background-color: #bffff2; padding: 10px;">모든 단어에 대한 문장을 생성했습니다.</p>', unsafe_allow_html=True)
            del st.session_state['words_list']
            st.session_state['learned_count'] = 0  # 학습 카운터 초기화
