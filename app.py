{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cd1c5c91-c07c-466f-956b-866908ecb5b3",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import streamlit as st\n",
    "from dotenv import load_dotenv\n",
    "import google.generativeai as gpt\n",
    "from functions import*\n",
    "\n",
    "# Load API Key from .env\n",
    "load_dotenv()\n",
    "genai.configure(api_key=os.getenv(\"GOOGLE_API_KEY\"))\n",
    "\n",
    "# Load your products.json\n",
    "def load_inventory():\n",
    "    try:\n",
    "        with open('products.json', 'r') as f:\n",
    "            return json.load(f)\n",
    "    except FileNotFoundError:\n",
    "        return {}\n",
    "\n",
    "inventory = load_inventory()\n",
    "\n",
    "st.title(\"👨‍🔧 Spare Parts Assistant (Gemini)\")\n",
    "\n",
    "# Sidebar for inventory status\n",
    "with st.sidebar:\n",
    "    st.write(f\"Inventory Loaded: {len(inventory)} items\")\n",
    "\n",
    "# Chat UI\n",
    "if \"messages\" not in st.session_state:\n",
    "    st.session_state.messages = []\n",
    "\n",
    "for msg in st.session_state.messages:\n",
    "    st.chat_message(msg[\"role\"]).write(msg[\"content\"])\n",
    "\n",
    "if prompt := st.chat_input():\n",
    "    st.session_state.messages.append({\"role\": \"user\", \"content\": prompt})\n",
    "    st.chat_message(\"user\").write(prompt)\n",
    "\n",
    "    # Use Gemini to generate a response with context\n",
    "    model = genai.GenerativeModel('gemini-pro')\n",
    "    \n",
    "    # Provide inventory as context to Gemini\n",
    "    context = f\"You are a spare parts dealer. Here is your inventory: {json.dumps(inventory)}. \"\n",
    "    context += \"If a user asks for a part, check if it fits their car and tell them the price.\"\n",
    "    \n",
    "    full_prompt = f\"{context}\\n\\nUser: {prompt}\"\n",
    "    response = model.generate_content(full_prompt)\n",
    "    \n",
    "    st.session_state.messages.append({\"role\": \"assistant\", \"content\": response.text})\n",
    "    st.chat_message(\"assistant\").write(response.text)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
