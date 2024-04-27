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
