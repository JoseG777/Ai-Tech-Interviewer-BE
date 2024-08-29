from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from database.models import User, UserHistory, DailyAttempts
import openai
import os
import logging
import jwt
from datetime import datetime, timezone, timedelta  
from functools import wraps

# Function Imports
from APIs.getLeetCode import getLeetCodeInfo
from APIs.generateProblems import generate_problem
from APIs.evaluateResponse import evaluate_response, evaluate_speech, parse_evaluation
from APIs.ai_response import get_ai_response
from determine_level import evaluate_technical_exam

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

openai.api_key = os.getenv("OPEN_AI_API_KEY")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1) 

logging.basicConfig(level=logging.DEBUG)


# Error Handlers
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


# ***************** Token Verification Decorator *****************
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            logging.debug("Token is missing!")
            return jsonify({"message": "Token is missing!"}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            logging.debug(f"Decoded token data: {data}")
            current_user = User.get_user(data['uid'])
            if not current_user:
                raise ValueError("User not found")
        except Exception as e:
            logging.error(f"Token is invalid: {str(e)}")
            return jsonify({"message": f"Token is invalid: {str(e)}"}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function



# **************************** SIGNING UP / SIGNING IN ****************************
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
@token_required
def new_user(current_user):
    try:
        data = request.get_json()
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
            current_user[0],  # Use UID from the authenticated user
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

    email_record = User.get_email(username)

    if email_record is not None:
        email = email_record[0] 
        return jsonify({"email": email}), 200
    else:
        return jsonify({"error": "Username not found"}), 404


@app.route("/api/authenticate", methods=["POST"])
def authenticate():
    data = request.get_json()
    uid = data.get("uid") 

    if not uid:
        return jsonify({"error": "Missing UID"}), 400

    user = User.get_user(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    token = jwt.encode(
        {'uid': uid, 'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION_DELTA']},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    response = make_response(jsonify({"message": "Authentication successful"}))
    response.set_cookie('token', token, httponly=True, secure=True, samesite='None')  

    return response, 200


@app.route("/api/logout", methods=["POST"])
@token_required
def logout(current_user):
    response = jsonify({"message": "Logout successful"})
    response.set_cookie('token', '', expires=0, httponly=True, secure=True, samesite='None') 
    return response



# **************************** AUTH CHECK ****************************
@app.route("/api/check_auth", methods=["GET"])
@token_required
def check_auth(current_user):
    return jsonify({"message": "Authenticated", "uid": current_user[0]}), 200


@app.route("/api/get_exam_status", methods=["GET", "POST"])
@token_required
def get_exam_status(current_user):
    try:
        exam_status = User.get_exam_status(current_user[0])
        return jsonify({"exam_status": exam_status}), 200
    except Exception as e:
        logging.error(f"Failed to get exam status: {str(e)}")
        return jsonify({"message": f"Failed to get exam status: {str(e)}"}), 500


# **************************** Problem generation / evaluation ****************************
@app.route("/api/generateProblem", methods=["POST"])
@token_required
def generate_problem_endpoint(current_user):
    try:
        data = request.get_json()
        language = data["language"]

        # Retrieve user's current goal and upcoming interview
        current_goal = current_user[9]
        upcoming_interview = current_user[10]

        # Extract beginner, intermediate, and advanced topics from current_user
        beginner_topics = current_user[11].split(",") if current_user[11] else []
        intermediate_topics = current_user[12].split(",") if current_user[12] else []
        advanced_topics = current_user[13].split(",") if current_user[13] else []

        skill_levels = {}

        for topic in beginner_topics:
            skill_levels[topic.strip()] = "Beginner"
        for topic in intermediate_topics:
            skill_levels[topic.strip()] = "Intermediate"
        for topic in advanced_topics:
            skill_levels[topic.strip()] = "Advanced"
        
        if not skill_levels:
            return jsonify({"message": "No skill levels available for the user."}), 400
        
        problem = generate_problem(
            skill_levels,
            current_goal,
            language,
            upcoming_interview,
        )

        return jsonify({"problem": problem})

    except Exception as e:
        logging.error(f"Failed to generate problem: {str(e)}")
        return jsonify({"message": f"Failed to generate problem: {str(e)}"}), 500


@app.route("/api/evaluateResponse", methods=["POST"])
@token_required
def evaluate_response_endpoint(current_user):
    try:
        data = request.get_json()
        problem = data["problem"]
        response = data["userResponse"]
        speech_input = data.get("speechInput", "N/A")

        if problem and response:
            code_evaluation = evaluate_response(problem, response)
            code_evaluation2, feedback, final_grade = parse_evaluation(code_evaluation)
            final_grade = int(final_grade)

            speech_evaluation2 = speech_feedback = final_speech_grade = None
            if speech_input != "N/A":
                speech_evaluation = evaluate_speech(problem, response, speech_input)
                speech_evaluation2, speech_feedback, final_speech_grade = parse_evaluation(speech_evaluation)
                final_speech_grade = int(final_speech_grade)

            UserHistory.update_history(
                current_user[0],
                problem,
                response,
                code_evaluation2,
                feedback,
                final_grade,
                speech_evaluation2,
                speech_feedback,
                final_speech_grade,
            )

            DailyAttempts.update_daily_attempts(current_user[0])

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
@token_required
def chat(current_user):
    try:
        data = request.get_json()
        user_message = data.get("message")
        problem = data.get("problem")
        previous_ai_response = data.get("previousAIResponse")

        ai_response = get_ai_response(user_message, problem, previous_ai_response)
        return jsonify({"ai_response": ai_response})
    except Exception as e:
        logging.error(f"Failed to get chat response: {str(e)}")
        return jsonify({"message": f"Failed to get chat response: {str(e)}"}), 500


@app.route("/api/grade_exam", methods=["POST"])
@token_required
def grade_exam(current_user):
    try:
        data = request.get_json()

        if not data or 'answers' not in data:
            return jsonify({"message": "Missing information"}), 400

        answers = data['answers']

        skill_levels = evaluate_technical_exam(answers)

        User.update_skill_levels(
            current_user[0],
            skill_levels["Beginner"],
            skill_levels["Intermediate"],
            skill_levels["Advanced"]
        )

        return jsonify({"message": "Exam graded successfully", "skill_levels": skill_levels}), 200

    except Exception as e:
        logging.error(f"Failed to grade exam: {str(e)}")
        return jsonify({"message": f"Failed to grade exam: {str(e)}"}), 500


# **************************** DELETE USER ****************************
@app.route("/api/deleteUser", methods=["POST"])
@token_required
def delete_user(current_user):
    try:
        User.remove_user(current_user[0])
        return jsonify({"message": "User removed successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to delete user: {str(e)}")
        return jsonify({"message": f"Failed to delete user: {str(e)}"}), 500


# **************************** Update info ****************************
@app.route("/api/updateGoal", methods=["POST"])
@token_required
def update_goal(current_user):
    try:
        data = request.get_json()
        goal = data["current_goal"]

        User.update_goal(current_user[0], goal)
        return jsonify({"message": "User's goal updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update goal: {str(e)}")
        return jsonify({"message": f"Failed to update goal: {str(e)}"}), 500


@app.route("/api/updateInterview", methods=["POST"])
@token_required
def update_interview(current_user):
    try:
        data = request.get_json()
        interview = data["upcoming_interview"]

        User.update_interview(current_user[0], interview)
        return jsonify({"message": "User's interview updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update interview: {str(e)}")
        return jsonify({"message": f"Failed to update interview: {str(e)}"}), 500


@app.route("/api/addLeetCode", methods=["POST"])
@token_required
def add_leetcode(current_user):
    try:
        data = request.get_json()
        leetcode_username = data.get("leetcode_username")

        if not leetcode_username:
            return jsonify({"message": "LeetCode username is required"}), 400

        User.update_leetcode_username(current_user[0], leetcode_username)
        return jsonify({"message": "LeetCode username updated successfully"}), 201
    except Exception as e:
        logging.error(f"Failed to update LeetCode username: {str(e)}")
        return jsonify({"message": f"Failed to update LeetCode username: {str(e)}"}), 500


# **************************** Get Info ****************************
@app.route("/api/getUsers", methods=["GET"])
@token_required
def get_user(current_user):
    try:
        code_grades = UserHistory.get_code_grades(current_user[0]) or []
        speech_grades = UserHistory.get_speech_grades(current_user[0]) or []
        attempts = UserHistory.count_history(current_user[0]) or []
        lc_stats = UserHistory.get_leetcode_stats(current_user[0]) or [0.0, 0.0, 0.0, 0.0]

        return jsonify(
            {
                "user": {
                    "username": current_user[2],
                    "leetcode_username": current_user[3] if current_user[3] else None,
                    "level_description": current_user[4],
                    "current_goal": current_user[9],
                    "upcoming_interview": current_user[10],
                    "signup_date": current_user[11],
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
@token_required
def get_user_history(current_user):
    try:
        history = UserHistory.get_user_history(current_user[0])
        return jsonify({"history": history})
    except Exception as e:
        logging.error(f"Failed to get user history: {str(e)}")
        return jsonify({"message": f"Failed to get user history: {str(e)}"}), 500


if __name__ == "__main__":
    from database.initialization import initialize_database

    initialize_database()
    app.run(debug=True, port=5000)
