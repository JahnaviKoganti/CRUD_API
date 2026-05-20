from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample in-memory database
tasks = [
   {
       "id": 1,
       "title": "Learn Flask",
       "completed": False
   }
]

# GET all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
   return jsonify(tasks)

# GET a single task
@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):

   for task in tasks:
       if task["id"] == id:
           return jsonify(task)

   return jsonify({"message": "Task not found"}), 404

# POST create a task
@app.route('/tasks', methods=['POST'])
def create_task():

   data = request.json

   new_task = {
       "id": len(tasks) + 1,
       "title": data["title"],
       "completed": False
   }

   tasks.append(new_task)

   return jsonify(new_task), 201

# PUT update a task
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):

   for task in tasks:

       if task["id"] == id:

           data = request.json

           task["title"] = data.get("title", task["title"])
           task["completed"] = data.get("completed", task["completed"])

           return jsonify(task)

   return jsonify({"message": "Task not found"}), 404

# DELETE a task
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):

   for task in tasks:

       if task["id"] == id:
           tasks.remove(task)

           return jsonify({
               "message": "Task deleted successfully"
           })

   return jsonify({"message": "Task not found"}), 404

if __name__ == '__main__':
   app.run(debug=True)
