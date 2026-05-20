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

# Sample tasks
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


# LOGIN
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

            password:
              type: string

    responses:
      200:
        description: Login successful

      400:
        description: Bad request

      401:
        description: Invalid credentials
    """

    data = request.get_json()

    # Empty body validation
    if not data:

        return jsonify({
            "message": "Request body is missing"
        }), 400

    # Required field validation
    if "username" not in data or "password" not in data:

        return jsonify({
            "message": "Username and password are required"
        }), 400

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


# GET ALL TASKS
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
        description: Success

      401:
        description: Unauthorized
    """

    current_user = get_jwt_identity()

    return jsonify({
        "logged_in_as": current_user,
        "tasks": tasks
    })


# GET SINGLE TASK
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


# CREATE TASK
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

    responses:
      201:
        description: Task created

      400:
        description: Bad request
    """

    data = request.get_json()

    # Empty body validation
    if not data:

        return jsonify({
            "message": "Request body is missing"
        }), 400

    # Required field validation
    if "title" not in data:

        return jsonify({
            "message": "Title is required"
        }), 400

    # Datatype validation
    if not isinstance(data["title"], str):

        return jsonify({
            "message": "Title must be a string"
        }), 400

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "completed": False
    }

    tasks.append(new_task)

    return jsonify(new_task), 201


# UPDATE TASK
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
        description: Task updated

      400:
        description: Bad request

      404:
        description: Task not found
    """

    data = request.get_json()

    # Empty body validation
    if not data:

        return jsonify({
            "message": "Request body is missing"
        }), 400

    for task in tasks:

        if task["id"] == id:

            # Validate title
            if "title" in data:

                if not isinstance(data["title"], str):

                    return jsonify({
                        "message": "Title must be a string"
                    }), 400

                task["title"] = data["title"]

            # Validate completed
            if "completed" in data:

                if not isinstance(data["completed"], bool):

                    return jsonify({
                        "message": "Completed must be true or false"
                    }), 400

                task["completed"] = data["completed"]

            return jsonify(task)

    return jsonify({
        "message": "Task not found"
    }), 404


# DELETE TASK
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
        description: Task deleted

      403:
        description: Admin only

      404:
        description: Task not found
    """

    claims = get_jwt()

    # Role validation
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
