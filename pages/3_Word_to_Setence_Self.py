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

def generate_sentence_with_word(word):
    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
        {
            "role": "system",
            "content": "You are an English tutor who generates sentences with a word when it is presented. When generating words, you should use easy and simple words that English beginners can know. You should make only 1 short sentence that you use a lot in your real life."
        },
        {
            "role": "user",
            "content": "laptop"
        },
        {
            "role": "assistant",
            "content": "I often use my laptop to check my email."
        },
        {
            "role": "user",
            "content": "coffee"
        },
        {
            "role": "assistant",
            "content": "I drink coffee every morning."
        },
        {
            "role": "user",
            "content": "TV"
        },
        {
            "role": "assistant",
            "content": "I watch TV with my family on Friday nights."
        },
        {
            "role": "user",
            "content": "fridge"
        },
        {
            "role": "assistant",
            "content": "I keep my juice in the fridge."
        },
        {
            "role": "user",
            "content": "table"
        },
        {
            "role": "assistant",
            "content": "We have dinner on the table at 6 pm."
        },
        {
            "role": "user",
            "content": "computer"
        },
        {
            "role": "assistant",
            "content": "My brother works on the computer all day."
        },
        {
            "role": "user",
            "content": "chair"
        },
        {
            "role": "assistant",
            "content": "My mom sits in the chair to read a book."
        },
        {
            "role": "user",
            "content": "easy"
        },
        {
            "role": "assistant",
            "content": "Learning English is easy for beginners."
        },
        {
            "role": "user",
            "content": "youtube"
        },
        {
            "role": "assistant",
            "content": "I often watch educational videos on YouTube."
        },
        {
            "role": "user",
            "content": "watch"
        },
        {
            "role": "assistant",
            "content": "I like to watch a movie on the weekend."
        },
        {
            "role": "user",
            "content": "apple"
        },
        {
            "role": "assistant",
            "content": "My favorite fruit is a juicy apple."
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
        )
        response = completion.choices[0].message.content
        # 응답 파싱
        lines = response.split('\n')
        english_sentence, korean_translation = None, None
        for line in lines:
            cleaned_line = line.strip().strip('"')
            if '**English:**' in cleaned_line:
                english_sentence = cleaned_line.replace('**English:**', '').strip().strip('"')
                english_sentence = english_sentence.replace('**', '')  # '**' 제거
            elif '**Korean:**' in cleaned_line:
                korean_translation = cleaned_line.replace('**Korean:**', '').strip().strip('"')
                korean_translation = korean_translation.replace('**', '')  # '**' 제거

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
