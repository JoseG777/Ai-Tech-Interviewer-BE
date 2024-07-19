from flask import Flask, request, jsonify
import database.db_funcs as db_funcs
from flask_cors import CORS

# Function Imports  
from APIs.getLeetCode import getLeetCodeInfo
from APIs.generateProblems import generate_problem
from APIs.evaluateResponse import evaluate_response

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/message", methods=["GET"])
def get_message():
    return jsonify({"message": "Hello from Flask!"})


@app.route("/api/createUser", methods=["POST"])
def create_user():
    data = request.get_json()
    uid = data["uid"]
    email = data["email"]
    leetcode_username = "N/A"
    user_level_description = "N/A"
 

    db_funcs.add_user(
        uid,
        email,
        leetcode_username,
        user_level_description
    )

    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/initialQuestions", methods=["POST"])
def new_user_info():
    '''
    easy_ratio, medium_ratio, hard_ratio, overall_ratio = getLeetCodeInfo(
        leetcode_username
    )
    '''

    pass

@app.route("/api/generateProblem", methods=["POST"])
def generate_problem_endpoint():
    data = request.get_json()
    uid = data["uid"]

    user = db_funcs.get_user_id(uid)

    print(user)

    print(user[0])

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_level_description = user[3]
    easy_ratio = user[4]
    medium_ratio = user[5]
    hard_ratio = user[6]
    overall_ratio = user[7]

    problem = generate_problem(
        user_level_description, easy_ratio, medium_ratio, hard_ratio, overall_ratio
    )
    return jsonify({"problem": problem})


@app.route("/api/evaluateResponse", methods=["POST"])
def evaluate_response_endpoint():
    data = request.get_json()
    problem = data["problem"]
    response = data["userResponse"]
    uid = data["uid"]
    # print(uid)

    if problem and response and uid:
        evaluation = evaluate_response(problem, response)

        # ADD FUNCTION TO SAVE TO DATABASE HERE paramaters should be (uid, problem, response, evaluation)
        db_funcs.update_history(uid, problem, response, evaluation)

        return jsonify({"evaluation": evaluation})

    return jsonify({"evaluation": "error"})


if __name__ == "__main__":
    db_funcs.initialize_database()
    app.run(debug=True, port=5000)
