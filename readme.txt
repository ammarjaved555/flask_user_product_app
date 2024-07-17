This API provides endpoints for user registration, login, access token generation, refresh token generation, and protected routes requiring a valid access token. It uses JWT (JSON Web Tokens) for securing API endpoints.

Base URL
http://localhost:8000

Endpoints
1. Register a User
URL: /register
Method: POST
Description: Register a new user.

Request Body:

json
Copy code
{
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
}
Response:

201 Created:
json
Copy code
{
    "message": "User created successfully",
    "access_token": "string",
    "refresh_token": "string"
}
400 Bad Request:
json
Copy code
{
    "message": "Missing required fields"
}
json
Copy code
{
    "message": "Email already registered. Please try with different email."
}
json
Copy code
{
    "message": "Passwords do not match"
}
500 Internal Server Error:
json
Copy code
{
    "message": "Database error occurred. Please try again."
}
2. Login a User
URL: /login
Method: POST
Description: Login an existing user.

Request Body:

json
Copy code
{
    "email": "string",
    "password": "string"
}
Response:

200 OK:
json
Copy code
{
    "message": "Login successful",
    "access_token": "string",
    "refresh_token": "string",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "date_created": "string"
    }
}
400 Bad Request:
json
Copy code
{
    "message": "Missing email or password"
}
401 Unauthorized:
json
Copy code
{
    "message": "Invalid email or password"
}
500 Internal Server Error:
json
Copy code
{
    "message": "An error occurred"
}
3. Refresh Access Token
URL: /refresh
Method: POST
Description: Refresh the access token using a valid refresh token.

Request Body:

json
Copy code
{
    "refresh_token": "string"
}
Response:

200 OK:
json
Copy code
{
    "access_token": "string"
}
400 Bad Request:
json
Copy code
{
    "message": "Missing refresh token"
}
401 Unauthorized:
json
Copy code
{
    "message": "Invalid or expired refresh token"
}
404 Not Found:
json
Copy code
{
    "message": "User not found"
}
500 Internal Server Error:
json
Copy code
{
    "message": "An error occurred"
}
4. Protected Route
URL: /protected
Method: GET
Description: Access a protected route that requires a valid access token.

Headers:

http
Copy code
Authorization: Bearer access_token
Response:

200 OK:
json
Copy code
{
    "message": "Hello, username. This is a protected route."
}
401 Unauthorized:
json
Copy code
{
    "message": "Token is missing!"
}
json
Copy code
{
    "message": "Token is invalid or expired!"
}
404 Not Found:
json
Copy code
{
    "message": "User not found"
}
500 Internal Server Error:
json
Copy code
{
    "message": "An error occurred"
}
5. Get All Users
URL: /users
Method: GET
Description: Retrieve a list of all registered users.

Response:

200 OK:
json
Copy code
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "password": "string",
        "confirm_password": "string",
        "date_created": "string"
    },
    ...
]
500 Internal Server Error:
json
Copy code
{
    "message": "An error occurred"
}
Notes
Ensure to replace "string" and "integer" with actual values when making requests.
JWT tokens should be included in the Authorization header as Bearer token.
The refresh_token has a longer lifespan compared to the access_token.
Example Usage
Register a New User
python
Copy code
import requests

url = 'http://localhost:8000/register'
payload = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password",
    "confirm_password": "password"
}

response = requests.post(url, json=payload)
print(response.json())
Login a User
python
Copy code
import requests

url = 'http://localhost:8000/login'
payload = {
    "email": "test@example.com",
    "password": "password"
}

response = requests.post(url, json=payload)
print(response.json())
Refresh Access Token
python
Copy code
import requests

url = 'http://localhost:8000/refresh'
refresh_token = 'your_refresh_token_here'

response = requests.post(url, json={'refresh_token': refresh_token})
print(response.json())
Access Protected Route
python
Copy code
import requests

url = 'http://localhost:8000/protected'
access_token = 'your_access_token_here'
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)
print(response.json())
This documentation provides a comprehensive overview of the available endpoints and how to use them effectively.