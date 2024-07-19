import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")


def generate_problem(
    user_level_description, easy_ratio, medium_ratio, hard_ratio, overall_ratio
):
    gpt_prompt = f"""
    Based on the following user profile, generate a coding problem. The problem should include the problem description, specifications, and a bare-bones function or class definition if necessary.
    
    - Level Description: {user_level_description}
    User LeetCode Submission Acceptance to Submission Count Profile Stats:
    - Easy Problem Ratio: {easy_ratio}
    - Medium Problem Ratio: {medium_ratio}
    - Hard Problem Ratio: {hard_ratio}
    - Overall Problem Ratio: {overall_ratio}

    Provide a Python interview problem based on the information above. If you provide a problem that needs class information, provide that as well. Make it simple very simple like a regular leetcode
    NO MARKDOWN RETURNS
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation
