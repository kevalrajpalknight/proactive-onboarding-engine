# Proactive Onboarding Engine API Documentation

This document provides the documentation for the Proactive Onboarding Engine API. The API is built with FastAPI and provides endpoints for user management and chat interactions.

The API documentation is also available through the following interactive UIs:

- [Swagger UI](/docs)
- [ReDoc](/redoc)

## Base URL

The API is served from the root of the application. All endpoints are prefixed with their respective router paths.

## Authentication

Most endpoints require authentication. Authentication is handled via JWT tokens. To authenticate, you must first obtain a token by using the `/users/login` endpoint. The token must then be included in the `Authorization` header of subsequent requests as a Bearer token.

Example: `Authorization: Bearer <your_token>`

---

## Users API

The Users API provides endpoints for user registration, login, and retrieval.

**Router Prefix:** `/users`

### `POST /users/`

- **Operation:** `create_user`
- **Description:** Creates a new user.
- **Request Body:**
  ```json
  {
    "full_name": "string",
    "email": "user@example.com",
    "password": "your_password",
    "profile": {}
  }
  ```
- **Responses:**
  - `200 OK`: Returns the newly created user's data (excluding password).
    ```json
    {
      "id": "user_uuid",
      "full_name": "string",
      "email": "user@example.com",
      "profile": {},
      "last_login": null,
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
    ```
  - `400 Bad Request`: If the email is already registered.

### `POST /users/login`

- **Operation:** `login_user`
- **Description:** Authenticates a user and returns a JWT token.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "your_password"
  }
  ```
- **Responses:**
  - `200 OK`: Returns a JWT token and user information.
    ```json
    {
      "token": "your_jwt_token",
      "user": {
        "id": "user_uuid",
        "full_name": "string",
        "email": "user@example.com",
        "profile": {},
        "last_login": "timestamp",
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    }
    ```
  - `401 Unauthorized`: If credentials are invalid.

### `GET /users/{user_id}`

- **Operation:** `read_user`
- **Description:** Retrieves a user's information by their ID.
- **Authentication:** Required.
- **Path Parameters:**
  - `user_id` (UUID): The ID of the user to retrieve.
- **Responses:**
  - `200 OK`: Returns the user's data.
  - `404 Not Found`: If the user is not found.

---

## Chats API

The Chats API handles all chat-related interactions, including creating chats, sending messages, and retrieving chat history.

**Router Prefix:** `/chats`

### `POST /chats/`

- **Operation:** `chat_interaction`
- **Description:** Handles a single chat interaction. It can create a new chat or continue an existing one.
- **Authentication:** Required.
- **Request Body:**
  ```json
  {
    "session_id": "chat_session_uuid",
    "message": "User's message"
  }
  ```
- **Behavior:**
  - If `session_id` is for a new chat, a new chat is created, a title is generated, and the first clarifying question is returned.
  - If `session_id` exists, the message is processed as an answer to the last question, and the next question is returned.
- **Responses:**
  - `200 OK`: Returns the next question or a completion message.
    ```json
    {
      "session_id": "chat_session_uuid",
      "question": "Next clarifying question from the AI?",
      "completed": false,
      "order": 1,
      "options": ["Option 1", "Option 2"],
      "question_type": "multiple_choice"
    }
    ```
    Or if completed:
    ```json
    {
      "session_id": "chat_session_uuid",
      "question": "Thank you for the information!",
      "completed": true
    }
    ```
  - `400 Bad Request`: If the message or session ID is invalid.

### `GET /chats/{session_id}/history`

- **Operation:** `get_chat_history`
- **Description:** Retrieves the full chat history for a given session ID.
- **Authentication:** Required.
- **Path Parameters:**
  - `session_id` (UUID): The ID of the chat session.
- **Responses:**
  - `200 OK`: Returns the chat history.
    ```json
    {
      "session_id": "chat_session_uuid",
      "title": "Chat Title",
      "status": "in_progress",
      "history": [
        {
          "question": "What is your goal?",
          "answer": "To learn FastAPI.",
          "order": 1
        }
      ]
    }
    ```
  - `403 Forbidden`: If the user is not authorized to access the chat.
  - `404 Not Found`: If the chat is not found.
