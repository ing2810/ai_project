import streamlit as st
st.title('나의 첫 웹서비스 만들기')
a=st.text_input('이름을 입력하세요')
b=st.selectbox('좋아하는 음식을 선택하라.',['휘낭시에','크레이프','에그타르트','케이크','스콘'])
if st.button('인삿말 생성'):
  st.write(a+'님, 안녕하냐? 반갑습니다.')
  st.info('반갑다.')
  st.warning(b+'음식을 좋아하시는군.')
  st.error('잘 부탁하다.')
