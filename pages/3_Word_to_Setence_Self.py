import streamlit as st
import pandas as pd
from groq import Groq

# 스트림릿 페이지 설정
st.title("🦜🔗 Word to Sentence")

# Groq API 클라이언트 초기화
client = Groq()

def load_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
        return pd.read_excel(uploaded_file)

def generate_sentence_with_word(word):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "When an English word is provided, you need to create one simple and easy English conversation sentence that is commonly used in everyday life. You also need to provide one Korean translation of the English conversation sentence you created."
                },
                {
                    "role": "user",
                    "content": word
                }
            ],
            temperature=0,
            max_tokens=1024,
            top_p=0,
            stream=False
        )
        response = completion.choices[0].text  # 수정된 부분: 'delta' 대신 'text' 사용
        english_sentence, korean_translation = response.strip().split('\n')
        return english_sentence, korean_translation
    except Exception as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        return None, None

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    if 'words_list' not in st.session_state or st.button("Restart"):
        df = load_file(uploaded_file)
        words_column = 'words'
        if df is not None and words_column in df.columns:
            st.session_state['words_list'] = df[words_column].dropna().tolist()
            st.session_state['learned_count'] = 0

    if st.session_state.get('words_list'):
        word = st.session_state['words_list'].pop(0)
        st.session_state['learned_count'] += 1
        with st.spinner('문장 생성중...'):
            english_sentence, korean_translation = generate_sentence_with_word(word)
            if english_sentence and korean_translation:
                st.markdown(f'<p style="font-size: 20px; text-align: center;">{english_sentence}</p>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size: 20px; text-align: center;">{korean_translation}</p>', unsafe_allow_html=True)
                st.markdown(f'공부한 단어 수: {st.session_state["learned_count"]}')

        if not st.session_state['words_list']:
            st.markdown('<p style="background-color: #bffff2; padding: 10px;">모든 단어에 대한 문장을 생성했습니다.</p>', unsafe_allow_html=True)
            del st.session_state['words_list']
            st.session_state['learned_count'] = 0  # 학습 카운터 초기화
