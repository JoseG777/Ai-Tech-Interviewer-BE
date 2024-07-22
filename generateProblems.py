
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPEN_AI_API_KEY')

def generate_problem(user_level_description, easy_ratio, medium_ratio, hard_ratio, overall_ratio):
    gpt_prompt = f"""
    users description: {user_level_description}
    to provide a coding question. The Format is: name of the problem (don't give an introduction 
    just write the name), description (don't label  the description with "description " , 3 example 
    test cases, and possible constraints. Make it every similar to the leetcode format. 

    Use the following user profile from their leetcode account to decide what question to return: 
        User LeetCode Submission Acceptance to Submission Count Profile Stats:
        - Easy Problem Ratio: {easy_ratio}
        - Medium Problem Ratio: {medium_ratio}
        - Hard Problem Ratio: {hard_ratio}
        - Overall Problem Ratio: {overall_ratio}

    Don't provide 
    the solution to the problem and NO MARKDOWN RETURNS.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation


"""
prompt:
users description: {I am a beginner and I want to focus  on dynamic programing}
to provide a coding question.The difficulty level should be "Medium" and write the difficulty
next to the name of the problem. the Format is: name of the problem (don't give an introduction 
just write the name), description (don't label  the description with "description " , 3 example 
test cases, and possible constraints. Make it every similar to the leetcode format. 

Use the following user profile from their leetcode account to decide what question to return: 
    User LeetCode Submission Acceptance to Submission Count Profile Stats:
    - Easy Problem Ratio: {4 easy level submitions }
    - Medium Problem Ratio: {1 meaium submition}
    - Hard Problem Ratio: {2 hard submitions}
    - Overall Problem Ratio: {7 overall submitions}

Don't provide 
the solution to the problem and NO MARKDOWN RETURNS.

"""