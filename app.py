from flask import Flask, request, jsonify
from flask_jwt_extended import get_jwt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

app = Flask(__name__)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

# Sample in-memory database
tasks = [
    {
        "id": 1,
        "title": "Learn Flask",
        "completed": False
    }
]

# Sample users
users = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    },
    {
        "username": "jahnavi",
        "password": "user123",
        "role": "user"
    }
]

# LOGIN ROUTE
@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    for user in users:
        
        if user["username"] == username and user["password"] == password:

            access_token = create_access_token(
                identity=username,
                additional_claims={
                    "role": user["role"]
                }
            )

            return jsonify({
                "message": "Login successful",
                "access_token": access_token
            }), 200

    return jsonify({
        "message": "Invalid username or password"
    }), 401


# GET all tasks (Protected)
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():

    current_user = get_jwt_identity()

    return jsonify({
        "logged_in_as": current_user,
        "tasks": tasks
    })


# GET a single task (Protected)
@app.route('/tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):

    for task in tasks:
        
        if task["id"] == id:
            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# POST create a task (Protected)
@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():

    data = request.get_json()

    if "title" not in data:
        
        return jsonify({
            "message": "Title is required"
        }), 400

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "completed": False
    }

    tasks.append(new_task)

    return jsonify(new_task), 201


# PUT update a task (Protected)
@app.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):

    for task in tasks:
        
        if task["id"] == id:

            data = request.get_json()

            task["title"] = data.get("title", task["title"])
            task["completed"] = data.get("completed", task["completed"])

            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# DELETE task (Admin only)
@app.route('/tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):

    claims = get_jwt()

    if claims["role"] != "admin":
        
        return jsonify({
            "message": "Access denied. Admins only."
        }), 403

    for task in tasks:
        
        if task["id"] == id:

            tasks.remove(task)

            return jsonify({
                "message": "Task deleted successfully"
            })

    return jsonify({
        "message": "Task not found"
    }), 404


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
