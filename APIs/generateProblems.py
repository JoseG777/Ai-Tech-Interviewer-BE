import openai
import os
from dotenv import load_dotenv
import random

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_API_KEY")


def generate_problem(
    skill_levels,  
    current_goal,
    language,
    upcoming_interview,
):
    # avoid empty lists
    valid_skill_levels = {k: v for k, v in skill_levels.items() if v}

    if not valid_skill_levels:
        return "No valid categories or skill levels available to generate a problem."

    category, user_level_description = random.choice(list(valid_skill_levels.items()))
    print("\n\n\n\n\n\n\n\n", category, "\n\n\n\n\n\n\n\n", user_level_description)

    interview_info = (
        f"Upcoming Interview: This problem should be tailored for an upcoming interview with {upcoming_interview}. PRIORITIZE THIS"
        if upcoming_interview != "N/A"
        else ""
    )

    gpt_prompt = f"""
    
        Generate a {language} coding problem tailored to a user's profile and skill level detailed below:
        
        Category: {category}
        Level: {user_level_description}
        Goal: {current_goal}
        {interview_info}

        Ensure the problem fits their skill set. If specific data structures or custom objects are needed, provide necessary class definitions or additional code. Only include the specified structure; do not add any notes or markdown. Output your response in the following this structure:

        Problem Description: A detailed description of the problem.

        Example 1:
        Input: [input example]
        Output: [expected output]

        Example 2:
        Input: [input example]
        Output: [expected output]

        Constraints: List all constraints.

        Function Signature: Provide the function signature. ONLY RETURN FUNCTION SIGNATURE. DO NOT RETURN ANYTHING FROM THIS POINT ON

    """

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": gpt_prompt}]
    )
    recommendation = response.choices[0].message["content"].strip()

    return recommendation
