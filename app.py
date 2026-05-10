import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread

# 1. Load Environment Variables

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found! Please add GOOGLE_API_KEY to your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# 2. Load Inventory
def load_inventory():
    if os.path.exists('products.json'):
        with open('products.json', 'r') as f:
            return json.load(f)
    return {}

inventory = load_inventory()

# 3. UI Setup
st.title("Spare Parts Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hi, I am Sabarmathi, your Spare Parts Assistant. How can I help you today?"
        }]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. Chat Logic
if prompt := st.chat_input("Ask about parts..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    
    # System Instruction
    context = f"You are a spare parts dealer. Inventory: {json.dumps(inventory)}. "
    context += "Check compatibility and price. Be helpful and concise."
    
    try:
        response = model.generate_content(f"{context}\nUser: {prompt}")
        print(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Gemini Error: {e}")
    # 1. Initialize Connection
    conn = st.connection("gsheets", type=GSheetsConnection)
    SHEET_ID = "1iQvaPlfJbLjOKNhxHzO116tm7wHa5rUueBP5pN10zLw"
    
    if prompt:
        # Split by lines instead of commas
        lines = prompt.split('\n')
        if len(lines) >= 3:
            details = {
                "Name": lines[0],
                "Address": lines[1],
                "Phone Number": lines[2],
                "Order Summary": "Chat Order"
            }
        client = conn.client
        sh = client.open_by_key(SHEET_ID)
        worksheet = sh.get_worksheet(0) # First tab
        
        # Append just the values as a list
        worksheet.append_row([details['Name'], details['Address'], details['Phone Number'], "Chat Order"])
   

# # Show assistant response
# st.session_state.messages.append({"role": "assistant", "content": response})
# st.chat_message("assistant").write(response)
