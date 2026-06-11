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
    context += "Check compatibility and price. Be helpful and concise. Remember previous chat history and response to the current message."   
    context += "Remember previous chat history and response to the current message.If user asked to order any spare parts, order the spare parts and ask them about the Name,delivery address and contact details."  

    content = "you are a assitant you checks the user_input response contains Name, Address and phone number if it is  convert should return only in json format Name: RR, Address: Chennai,Phone: +918883916171, if user_input doest contain name and phone number then return only in Single character 'N'.Remember previous chat history and response to the current message."

    try:
        lead = model.generate_content(f"{content}\nUser: {prompt}")
        #st.chat_message("assistant").write(lead.text)
        print(lead.text)
    except Exception as e:
        st.error(f"Gemini Error: {e}")
    if lead.text != 'N':    
        dict_lead = json.loads(lead.text)
        print("Lead Type", type(dict_lead))
        
        if type(dict_lead) is dict:            
            def save_data_to_gsheets(dict_lead):
                # 1. Connect to GSheets
                conn = st.connection("gsheets", type=GSheetsConnection)
                SHEET_ID = "https://docs.google.com/spreadsheets/d/1iQvaPlfJbLjOKNhxHzO116tm7wHa5rUueBP5pN10zLw/edit"
                
                # 2. Read existing data
                existing_data = conn.read(spreadsheet=SHEET_ID, ttl=0)
                
                # 3. Create a DataFrame from the dictionary
                new_row = pd.DataFrame([dict_lead])
                
                # 4. Combine and update the sheet
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_ID, data=updated_df)   
                
                st.success("Contact details successfully sent to the sales team!")
            # if isinstance(dict_lead, dict) and "name" in dict_lead:
            #     # Save the details
            save_data_to_gsheets(dict_lead)
                
                # Reset your chat flags
            st.session_state.awaiting_info = False
        else:
          print("This is not dictionary")
    else:
        print("No Lead captured")
    try:
        response = model.generate_content(f"{context}\nUser: {prompt}")
        print(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Gemini Error: {e}")
    # if prompt:
    #     order_keywords = ["order", "purchase", "buy", "checkout", "get this","name","address","phone"]
    #     user_data = prompt.split(",")
    #     if any(word in prompt.lower() for word in order_keywords):
    #         st.warning("Please provide Name, Address, and Phone separated by commas.")
    #     elif len(user_data) == 3:
    #         def save_to_gsheets(name, address, phone,part_info):
    #             # Create a new row of data
    #             new_data = pd.DataFrame([{
    #                 "Name": name,
    #                 "Address": address,
    #                 "Phone": phone,
    #                 "Order_Details": part_info
    #             }])
    #             df = conn.read(spreadsheet=SHEET_ID, ttl=0)
                         
    #             # 3. Add the new row to the old data
    #             # fillna('') prevents errors if your sheet has empty cells
    #             updated_df = pd.concat([df, new_data], ignore_index=True).fillna("")
            
    #             # 4. Save it back to Google Sheets
    #             conn.update(spreadsheet=SHEET_ID, data=updated_df)            
            
    #         if len(user_data) == 3:
    #             name, address, phone = [item.strip() for item in user_data]
    #             save_to_gsheets(name, address, phone, "User requested order")
    #             st.session_state.awaiting_info = False
    #         else:
    #             st.warning("Please provide Name, Address, and Phone separated by commas.")


# # Show assistant response
# st.session_state.messages.append({"role": "assistant", "content": response})
# st.chat_message("assistant").write(response)
