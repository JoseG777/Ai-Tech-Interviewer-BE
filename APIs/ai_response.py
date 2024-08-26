import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")

def get_ai_response(user_message, problem, previous_ai_response):
    if not previous_ai_response:
        previous_ai_response = ""
    try:
        system_prompt = f"""
        You are an interview assistant. You are presenting a coding problem to the user and helping them through the problem.
        You must not give away the solution directly. If the user asks for hints, provide only subtle hints that guide them in the right direction. 
        Only give hints if the user provides context about their current progress or what they have tried so far. Also, don't answer more than what is needed. 
        If a user asks something that can be answered in a yes or no response, return just yes or no.

        Make your answers short and concise. No more than 2 sentences.

        Here is the problem:
        {problem}

        Previous AI Response: {previous_ai_response}

        User: {user_message}

        Remember, do not give the solution directly.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        ai_response = response.choices[0].message["content"].strip()
        print("AI Response:", ai_response) 
        return ai_response

    except Exception as e:
        print("Error in get_ai_response:", str(e))
        return "Sorry, there was an error generating the response."
