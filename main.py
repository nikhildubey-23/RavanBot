import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import pyperclip
import sqlite3
from datetime import datetime
import hashlib

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Create a function to create a new database for each user
def create_database(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 question TEXT, 
                 answer TEXT, 
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

# Create a function to save user history to the database
def save_to_history(email, question, answer):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO user_history (question, answer, timestamp) VALUES (?, ?, ?)", (question, answer, timestamp))
    conn.commit()
    conn.close()

# Create a function to view user history from the database
def view_history(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_history")
    rows = c.fetchall()
    for row in rows:
        st.write(f"Question: {row[1]}")
        st.write(f"Answer: {row[2]}")
        st.write(f"Timestamp: {row[3]}")
        st.write("")
    conn.close()

# Create a function to get user input
def get_user_input():
    userInput = st.text_input("Enter your question")
    return userInput

# Create a function to create a prompt
def create_prompt():
    prompt_template = """
Ravan Offensive Security AI Assistant:
You are an expert in cybersecurity and can provide security solutions to users.
You can write code in Python and other languages.
You can understand English languages.
You are a very good web developer and code designer.
Your goal is to assist users with their cybersecurity needs.
You provide answer only for the asked question no need of extra information.
Your developer name is Ravan
Please respond to the following prompt:
{input}
"""
    
    return PromptTemplate.from_template(prompt_template)

# Create a function to copy to clipboard
def copy_to_clipboard(text):
    pyperclip.copy(text)
    st.write("Copied to Clipboard!")

# Create a function to clear history
def clear_history(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute("DELETE FROM user_history")
    conn.commit()
    conn.close()
    st.write("History cleared successfully!")

# Create a main function
def main():
    st.title("Ravan Offensive Security AI Assistant")
    email = "default_user"
    if not os.path.exists(f'{email}.db'):
        create_database(email)
    userInput = get_user_input()
    if st.button("Get Answer"):
        llm = ChatGroq(
            temperature=0, 
            groq_api_key=GROQ_API_KEY, 
            model_name="llama-3.1-8b-instant"
        )
        prompt_extract = create_prompt()
        chain_extract = prompt_extract | llm 
        res = chain_extract.invoke(userInput)
        output = res.content
        st.session_state.output = output
        st.write(output)
        save_to_history(email, userInput, output)
    if st.button("Copy to Clipboard"):
        if 'output' in st.session_state:
            copy_to_clipboard(st.session_state.output)
        else:
            st.write("Please generate the output first.")
    if st.button("View History"):
        view_history(email)
    if st.button("Clear History"):
        clear_history(email)

if __name__ == "__main__":
    main()