import streamlit as st

def main():
    st.title('Search a Udemy course')
    search = st.text_input('Enter search words:')

if __name__ == '__main__':
    main()