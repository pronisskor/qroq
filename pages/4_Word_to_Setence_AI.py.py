from langchain.llms import OpenAI
import streamlit as st
import openai
import pandas as pd
import random
import os

# Streamlit 페이지 타이틀 설정
st.title("🦜🔗 Word to Sentence AI")

# 사이드바 설정
with st.sidebar:
    # 사용자로부터 OpenAI API 키 입력받기
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("OpenAI API 키 받으러 가기 [여기 클릭](https://platform.openai.com/account/api-keys)")

# openai 라이브러리에 API 키 설정
if openai_api_key:
    openai.api_key = openai_api_key
    langchain_openai = OpenAI(api_key=openai_api_key)

if 'start' not in st.session_state:
    st.session_state['start'] = False

if 'ai_words_list' not in st.session_state or 'ai_learned_count' not in st.session_state:
    st.session_state['ai_words_list'] = []
    st.session_state['ai_learned_count'] = 0

def load_words():
    file_name = 'http://ewking.kr/AE/word_sentence.xlsx'
    if file_name.endswith('.csv'):
        df = pd.read_csv(file_name)
    elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        df = pd.read_excel(file_name)
    words_column = 'words'
    if df is not None and words_column in df.columns:
        st.session_state['ai_words_list'] = df[words_column].dropna().tolist()
        random.shuffle(st.session_state['ai_words_list'])

def generate_sentence_with_word(word):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a conversation sentence generator."},
                {"role": "user", "content": f"Please create a short and simple sentence using the word '{word}'."}
            ]
        )
        english_sentence = response.choices[0].message.content

        translation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator from English to Korean."},
                {"role": "user", "content": f"Translate this sentence into Korean: '{english_sentence}'"}
            ]
        )
        korean_translation = translation_response.choices[0].message.content

        return english_sentence, korean_translation
    except Exception as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        return None, None

def restart_study():
    if st.button('New Generate'):
        st.session_state['start'] = False
        st.session_state['ai_words_list'] = []
        st.session_state['ai_learned_count'] = 0
        load_words()
        st.session_state['start'] = True

restart_study()

if st.session_state['start'] and st.session_state.get('ai_words_list'):
    random_word = st.session_state['ai_words_list'].pop(0)
    st.session_state['ai_learned_count'] += 1  # 학습한 단어 카운트 증가
    with st.spinner('문장 생성중...'):
        english_sentence, korean_translation = generate_sentence_with_word(random_word)
        if english_sentence and korean_translation:
            highlighted_english_sentence = english_sentence.replace(random_word, f'<strong>{random_word}</strong>')
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{highlighted_english_sentence}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{korean_translation}</p>', unsafe_allow_html=True)
            st.markdown(f'공부한 단어 수: {st.session_state["ai_learned_count"]}')  # 학습한 단어 수 표시

    if st.button('다음 단어') or not st.session_state.get('ai_words_list'):
        if not st.session_state['ai_words_list']:
            st.markdown(f'<p style="background-color: #bffff2; padding: 10px;">모든 단어에 대한 문장을 생성했습니다.<br>다시 시작하려면 다시시작 버튼을 누르세요.</p>', unsafe_allow_html=True)
            st.session_state['start'] = False
            st.session_state['ai_words_list'] = []
            st.session_state['ai_learned_count'] = 0
            load_words()  # 다시 시작하려면 단어 목록을 다시 로드
            st.session_state['start'] = True