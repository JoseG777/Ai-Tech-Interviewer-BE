from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import User, UserHistory, DailyAttempts
import openai
import os
import logging

# Function Imports
from APIs.getLeetCode import getLeetCodeInfo
from APIs.generateProblems import generate_problem
from APIs.evaluateResponse import evaluate_response, evaluate_speech, parse_evaluation
from APIs.ai_response import get_ai_response
from determine_level import evaluate_technical_exam


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

openai.api_key = os.getenv("OPEN_AI_API_KEY")

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({"message": "Application is running."}), 200


#**************************** SIGNING UP / SIGNING IN ****************************
@app.route("/api/createUser", methods=["POST"])
def create_user():
    data = request.get_json()
    uid = data.get("uid")
    email = data.get("email")
    username = data["username"]

    if not uid or not email:
        return jsonify({"message": "Missing uid or email"}), 400

    try:
        leetcode_username = None
        user_level_description = "N/A"
        User.add_user(uid, username, email, leetcode_username, user_level_description)

        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        logging.error(f"Failed to create user: {str(e)}")
        return jsonify({"message": f"Failed to create user: {str(e)}"}), 500


@app.route("/api/newUser", methods=["POST"])
def new_user():
    try:
        data = request.get_json()
        uid = data["uid"]
        leetcode_username = data["leetcode_username"]
        coding_level = data["coding_level"]
        goal = data["goal"]
        upcoming_interview = data["upcoming_interview"]

        overall_ratio, easy_ratio, medium_ratio, hard_ratio = 0.0, 0.0, 0.0, 0.0

        if leetcode_username:
            leetcode_info = getLeetCodeInfo(leetcode_username)
            if leetcode_info != "N/A":
                overall_ratio, easy_ratio, medium_ratio, hard_ratio = leetcode_info

        User.update_user(
            uid,
            leetcode_username,
            coding_level,
            goal,
            upcoming_interview,
            overall_ratio,
            easy_ratio,
            medium_ratio,
            hard_ratio,
        )

        return jsonify({"message": "New user info received"}), 201
    except Exception as e:
        logging.error(f"Failed to update user: {str(e)}")
        return jsonify({"message": f"Failed to update user: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def log_user():
    data = request.get_json()
    username = data.get("username")
    email = User.get_email(username)

    if email is not None:
        return jsonify({"email": email[0]}), 201
    else:
        return jsonify({"error": "Username not found"}), 404
    

@app.route("/api/get_exam_status", methods=["POST"])
def get_exam_status():
    try:
        data = request.get_json()
        uid = data.get("uid")
        if not uid:
            return jsonify({"message": "Missing uid"}), 400

        exam_status = User.get_exam_status(uid)
        if exam_status is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"exam_status": exam_status}), 200

    except Exception as e:
        logging.error(f"Failed to get exam status: {str(e)}")
        return jsonify({"message": f"Failed to get exam status: {str(e)}"}), 500


#**************************** Problem generation / evaluation ****************************
@app.route("/api/generateProblem", methods=["POST"])
def generate_problem_endpoint():
    try:
        data = request.get_json()
        uid = data["uid"]
        language = data["language"]

        user = User.get_user(uid)

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_level_description = user[4]
        current_goal = user[9]
        upcoming_interview = user[10]

        problem = generate_problem(
            user_level_description,
            current_goal,
            language,
            upcoming_interview,
        )
        return jsonify({"problem": problem})
    except Exception as e:
        logging.error(f"Failed to generate problem: {str(e)}")
        return jsonify({"message": f"Failed to generate problem: {str(e)}"}), 500


@app.route("/api/evaluateResponse", methods=["POST"])
def evaluate_response_endpoint():
    try:
        data = request.get_json()
        problem = data["problem"]
        response = data["userResponse"]
        uid = data["uid"]
        speech_input = data.get("speechInput", "N/A")

        if problem and response and uid:
            code_evaluation = evaluate_response(problem, response)
            code_evaluation2, feedback, final_grade = parse_evaluation(code_evaluation)
            final_grade = int(final_grade)

            speech_evaluation2 = speech_feedback = final_speech_grade = None
            if speech_input != "N/A":
                speech_evaluation = evaluate_speech(problem, response, speech_input)
                speech_evaluation2, speech_feedback, final_speech_grade = (
                    parse_evaluation(speech_evaluation)
                )
                final_speech_grade = int(final_speech_grade)

            UserHistory.update_history(
                uid,
                problem,
                response,
                code_evaluation2,
                feedback,
                final_grade,
                speech_evaluation2,
                speech_feedback,
                final_speech_grade,
            )

            DailyAttempts.update_daily_attempts(uid)

            response_data = {
                "code_evaluation": {
                    "evaluation": code_evaluation2,
                    "feedback": feedback,
                    "final_grade": final_grade,
                },
                "speech_evaluation": (
                    {
                        "evaluation": speech_evaluation2,
                        "feedback": speech_feedback,
                        "final_grade": final_speech_grade,
                    }
                    if speech_input != "N/A"
                    else None
                ),
            }

            return jsonify(response_data)

        return jsonify({"evaluation": "error"})
    except Exception as e:
        logging.error(f"Failed to evaluate response: {str(e)}")
        return jsonify({"message": f"Failed to evaluate response: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        problem = data.get("problem")
        previous_ai_response = data.get("previousAIResponse")  
        
        print("Received previous AI response:", previous_ai_response) 
        
        ai_response = get_ai_response(user_message, problem, previous_ai_response)
        
        print("Generated AI response:", ai_response)
        return jsonify({"ai_response": ai_response})
    except Exception as e:
        logging.error(f"Failed to get chat response: {str(e)}")
        return jsonify({"message": f"Failed to get chat response: {str(e)}"}), 500


@app.route("/api/grade_exam", methods=["POST"])
def grade_exam():
    try:
        data = request.get_json()
        
        if not data or 'answers' not in data or 'uid' not in data:
            return jsonify({"message": "Missing information"}), 400
        
        answers = data['answers']
        uid = data['uid']
        
        skill_levels = evaluate_technical_exam(answers)
        
        User.update_skill_levels(
            uid,
            skill_levels["Beginner"],
            skill_levels["Intermediate"],
            skill_levels["Advanced"]
        )

        return jsonify({"message": "Exam graded successfully", "skill_levels": skill_levels}), 200
        
    except Exception as e:
        logging.error(f"Failed to grade exam: {str(e)}")
        return jsonify({"message": f"Failed to grade exam: {str(e)}"}), 500

    

#**************************** DELETE USER ****************************
@app.route("/api/deleteUser", methods=["POST"])
def delete_user():
    try:
        data = request.get_json()
        uid = data.get("uid")

        User.remove_user(uid)
        return jsonify({"message": "User removed successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to delete user: {str(e)}")
        return jsonify({"message": f"Failed to delete user: {str(e)}"}), 500


#**************************** Update info ****************************
@app.route("/api/updateGoal", methods=["POST"])
def update_goal():
    try:
        data = request.get_json()
        uid = data["uid"]
        goal = data["current_goal"]

        User.update_goal(uid, goal)
        return jsonify({"message": "User's goal updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update goal: {str(e)}")
        return jsonify({"message": f"Failed to update goal: {str(e)}"}), 500


@app.route("/api/updateInterview", methods=["POST"])
def update_interview():
    try:
        data = request.get_json()
        uid = data["uid"]
        interview = data["upcoming_interview"]

        User.update_interview(uid, interview)
        return jsonify({"message": "User's interview updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update interview: {str(e)}")
        return jsonify({"message": f"Failed to update interview: {str(e)}"}), 500


'''
@app.route("/api/updateLevel", methods=["POST"])
def update_level():
    try:
        data = request.get_json()
        uid = data["uid"]
        level_description = data["level_description"]

        User.update_level(uid, level_description)
        return jsonify({"message": "User's level updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update level: {str(e)}")
        return jsonify({"message": f"Failed to update level: {str(e)}"}), 500
'''


#**************************** Get Info ****************************
@app.route("/api/getUsers", methods=["GET"])
def get_user():
    try:
        uid = request.args.get("uid")
        user = User.get_user(uid)
        if not user:
            return jsonify({"error": "User not found"}), 404

        code_grades = UserHistory.get_code_grades(uid)
        speech_grades = UserHistory.get_speech_grades(uid)
        attempts = UserHistory.count_history(uid)
        lc_stats = UserHistory.get_leetcode_stats(uid)

        return jsonify(
            {
                "user": {
                    "username": user[2],
                    "leetcode_username": user[3] if user[3] else None, 
                    "level_description": user[4],
                    "current_goal": user[9],
                    "upcoming_interview": user[10],
                    "signup_date": user[11],
                },
                "code_grades": code_grades,
                "speech_grades": speech_grades,
                "attempts": attempts,
                "stats": lc_stats
            }
        )
    except Exception as e:
        logging.error(f"Failed to get user: {str(e)}")
        return jsonify({"message": f"Failed to get user: {str(e)}"}), 500


@app.route("/api/getUserHistory", methods=["GET"])
def get_user_history():
    try:
        uid = request.args.get("uid")
        user = User.get_user(uid)
        if not user:
            return jsonify({"error": "User not found"}), 404

        history = UserHistory.get_user_history(uid)

        return jsonify({"history": history})
    except Exception as e:
        logging.error(f"Failed to get user history: {str(e)}")
        return jsonify({"message": f"Failed to get user history: {str(e)}"}), 500


if __name__ == "__main__":
    from database.initialization import initialize_database

    initialize_database()
    app.run(debug=True, port=5000)
