import streamlit as st
import pandas as pd
import random

with st.sidebar:
    
    "[Open AI API 키 받으러 가기](https://platform.openai.com/account/api-keys)"

# 스트림릿 앱의 제목 설정
st.title("영어 단어 퀴즈")

# 데이터 파일의 URL을 코드에 직접 삽입
file_url = 'http://ewking.kr/AE/word_quiz.xlsx'  # 실제 URL로 교체 필요

# 파일 URL 확장자에 따라 적절한 pandas 함수를 사용하여 파일 로드
if file_url.endswith('.csv'):
    df = pd.read_csv(file_url)
elif file_url.endswith('.xls') or file_url.endswith('.xlsx'):
    df = pd.read_excel(file_url)

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
            st.write("퀴즈를 다시 시작하려면 'New Quiz' 버튼을 클릭하세요.")


    if st.session_state.current_index != -1:
        question = st.session_state.quiz_data[st.session_state.current_index]['question']
        answer = st.session_state.quiz_data[st.session_state.current_index]['answer'].strip().lower()

        st.write(f"문제 {st.session_state.quiz_number}: {question}")

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