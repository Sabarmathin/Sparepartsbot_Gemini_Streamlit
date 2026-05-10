import streamlit as st
import os
import json
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

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
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Gemini Error: {e}")

#5.Adding order details to gsheets
# 1. Setup Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Collect Data from User
with st.form("order_form"):
    name = st.text_input("Name")
    address = st.text_area("Address")
    phone = st.text_input("Phone Number")
    summary = st.text_area("Order Summary")
    
    submit_button = st.form_submit_button("Submit Order")

if submit_button:
    # 3. Fetch existing data
    existing_data = conn.read()
    
    # 4. Create a new row (ensure the column names match your sheet exactly)
    new_order = pd.DataFrame([{
        "Name": name,
        "Address": address,
        "Phone Number": phone,
        "Order Summary": summary
    }])
    
    # 5. Add new row to existing data
    updated_df = pd.concat([existing_data, new_order], ignore_index=True)
    
    # 6. Update the Google Sheet
    conn.update(data=updated_df)
    
    st.success("Order added successfully!")
