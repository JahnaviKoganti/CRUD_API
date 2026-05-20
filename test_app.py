from app import app

client = app.test_client()


# Generate JWT token
def get_token():

   response = client.post('/login', json={
       "username": "admin",
       "password": "admin123"
   })

   data = response.get_json()

   return data["access_token"]


# TEST LOGIN
def test_login():

   response = client.post('/login', json={
       "username": "admin",
       "password": "admin123"
   })

   assert response.status_code == 200


# TEST GET TASKS
def test_get_tasks():

   token = get_token()

   response = client.get(
       '/tasks',
       headers={
           "Authorization": f"Bearer {token}"
       }
   )

   assert response.status_code == 200


# TEST CREATE TASK
def test_create_task():

   token = get_token()

   response = client.post(
       '/tasks',
       json={
           "title": "Learn Testing"
       },
       headers={
           "Authorization": f"Bearer {token}"
       }
   )

   assert response.status_code == 201


# TEST UPDATE TASK
def test_update_task():

   token = get_token()

   response = client.put(
       '/tasks/1',
       json={
           "title": "Updated Task",
           "completed": True
       },
       headers={
           "Authorization": f"Bearer {token}"
       }
   )

   assert response.status_code == 200


# TEST DELETE TASK
def test_delete_task():

   token = get_token()

   response = client.delete(
       '/tasks/1',
       headers={
           "Authorization": f"Bearer {token}"
       }
   )

   assert response.status_code == 200
