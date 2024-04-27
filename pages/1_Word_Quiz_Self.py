import streamlit as st
import pandas as pd
import random

with st.sidebar:
    "OpenAI API 키 받으러 가기"    

st.title("영어 단어 퀴즈")

# 파일 업로더 위젯, CSV 및 Excel 파일 지원
uploaded_file = st.file_uploader("Excel, CSV 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    # 파일 확장자에 따라 적절한 pandas 함수를 사용하여 파일 로드
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = df.to_dict('records')
        st.session_state.used_indexes = []
        st.session_state.current_index = -1
        st.session_state.quiz_number = 0
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0

    if st.button('New Quiz'):
        # 모든 상태 초기화
        st.session_state.used_indexes = []
        st.session_state.current_index = -1
        st.session_state.quiz_number = 0
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0
        st.session_state['다음 문제'] = False  # '다음 문제' 상태도 초기화

        # 첫 문제 선택
        if len(st.session_state.quiz_data) > 0:
            st.session_state.current_index = random.choice(range(len(st.session_state.quiz_data)))
            st.session_state.used_indexes.append(st.session_state.current_index)
            st.session_state.quiz_number += 1

    if '다음 문제' in st.session_state and st.session_state['다음 문제']:
        if st.session_state.quiz_number < len(st.session_state.quiz_data):
            remaining_indexes = [i for i in range(len(st.session_state.quiz_data)) if i not in st.session_state.used_indexes]
            st.session_state.current_index = random.choice(remaining_indexes)
            st.session_state.used_indexes.append(st.session_state.current_index)
            st.session_state.quiz_number += 1
        else:
            # 모든 문제를 풀었을 때, 결과 출력 부분을 수정하여 정답과 오답 수가 정확하게 표시되도록 함
            st.write(f"모든 문제를 풀었습니다! 정답: {st.session_state.correct_answers}, 오답: {st.session_state.quiz_number - st.session_state.correct_answers}")
            st.session_state.used_indexes = []
            st.session_state.quiz_number = 0
            st.write("다시 복습하려면 'New Quiz' 버튼을 클릭하세요.")


    if st.session_state.current_index != -1:
        question = st.session_state.quiz_data[st.session_state.current_index]['question']
        answer = st.session_state.quiz_data[st.session_state.current_index]['answer'].strip().lower()

        st.markdown(f"<h5 style='font-weight:bold; text-align:center;'>문제 {st.session_state.quiz_number}: {question}</h5>", unsafe_allow_html=True)

        with st.form(key='answer_form'):
            user_answer = st.text_input("답을 입력하세요.", value="", key=f"user_answer_{st.session_state.current_index}")
            submit_button = st.form_submit_button('답변 제출')
            if submit_button:
                if user_answer.lower() == answer:
                    st.success("정답입니다!")
                    st.session_state.correct_answers += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {answer}입니다.")
                    st.session_state.incorrect_answers += 1
                # 다음 문제로 넘어갈 준비
                st.session_state['다음 문제'] = True
    else:
        st.session_state['다음 문제'] = False

    if st.session_state.current_index != -1 and len(st.session_state.used_indexes) < len(st.session_state.quiz_data):
        if st.button('다음 문제'):
            st.session_state['다음 문제'] = False