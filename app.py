from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from flasgger import Swagger

app = Flask(__name__)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

# Swagger Configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Task Management API",
        "description": "Flask API with JWT Authentication",
        "version": "1.0"
    },

    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: Bearer <your_token>"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=template)

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
    """
    User Login
    ---
    tags:
      - Authentication

    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: admin

            password:
              type: string
              example: admin123

    responses:
      200:
        description: Login successful

      401:
        description: Invalid username or password
    """

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


# GET all tasks
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get All Tasks
    ---
    tags:
      - Tasks

    security:
      - BearerAuth: []

    responses:
      200:
        description: Successfully retrieved tasks

      401:
        description: Unauthorized access
    """

    current_user = get_jwt_identity()

    return jsonify({
        "logged_in_as": current_user,
        "tasks": tasks
    })


# GET single task
@app.route('/tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):
    """
    Get Single Task
    ---
    tags:
      - Tasks

    security:
      - BearerAuth: []

    parameters:
      - name: id
        in: path
        type: integer
        required: true

    responses:
      200:
        description: Task found

      404:
        description: Task not found
    """

    for task in tasks:

        if task["id"] == id:
            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# CREATE task
@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create Task
    ---
    tags:
      - Tasks

    security:
      - BearerAuth: []

    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            title:
              type: string
              example: Learn JWT

    responses:
      201:
        description: Task created successfully

      400:
        description: Bad request
    """

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


# UPDATE task
@app.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    """
    Update Task
    ---
    tags:
      - Tasks

    security:
      - BearerAuth: []

    parameters:
      - name: id
        in: path
        type: integer
        required: true

      - in: body
        name: body
        schema:
          properties:
            title:
              type: string

            completed:
              type: boolean

    responses:
      200:
        description: Task updated successfully

      404:
        description: Task not found
    """

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
    """
    Delete Task
    ---
    tags:
      - Tasks

    security:
      - BearerAuth: []

    parameters:
      - name: id
        in: path
        type: integer
        required: true

    responses:
      200:
        description: Task deleted successfully

      403:
        description: Admin access required

      404:
        description: Task not found
    """

    claims = get_jwt()

    # Role check
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
