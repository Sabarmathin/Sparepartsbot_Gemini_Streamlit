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
# 1. Initialize Connection (Uses secrets.toml or Streamlit secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Logic to save details
def save_to_gsheets(name, address, phone, part_info):
    # Create a new row of data
    new_data = pd.DataFrame([{
        "Name": name,
        "Address": address,
        "Phone": phone,
        "Order_Details": part_info
    }])
    
    # Read existing data
    existing_data = conn.read()
    
    # Append and update
    updated_df = pd.concat([existing_data, new_data], ignore_index=True)
    conn.update(data=updated_df)
    st.success("Order details saved to Google Sheets!")

# 3. Integration in your Chatbot loop
if st.session_state.awaiting_info:
    # Assuming user provides: "Sairam, 123 Main St, 9876543210"
    user_data = prompt.split(",") 
    if len(user_data) == 3:
        name, address, phone = [item.strip() for item in user_data]
        save_to_gsheets(name, address, phone, "User requested order")
        st.session_state.awaiting_info = False
    else:
        st.warning("Please provide Name, Address, and Phone separated by commas.")
