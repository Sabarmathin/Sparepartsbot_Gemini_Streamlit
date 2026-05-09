{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5b437e81-433d-4a35-81d3-bdc655d280e0",
   "metadata": {},
   "outputs": [],
   "source": [
    "def map_role(role):\n",
    "    if role == \"model\":\n",
    "        return \"assistant\"\n",
    "    else:\n",
    "        return role\n",
    "\n",
    "def fetch_gemini_response(user_query):\n",
    "    # Use the session's model to generate a response\n",
    "    response = st.session_state.chat_session.model.generate_content(user_query)\n",
    "    print(f\"Gemini's Response: {response}\")\n",
    "    return response.parts[0].text"
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
